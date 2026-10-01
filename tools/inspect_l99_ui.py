"""Read-only, offline L99 UI-image inspector. Never opens USB, HID or COM.

Requires Pillow and numpy. Example:
python inspect_l99_ui.py recovered_screen_20260525/UartTFT-II_Flash.bin ui_inspection
"""
from pathlib import Path
import collections
import csv
import hashlib
import json
import struct
import sys
import numpy as np
from PIL import Image, ImageDraw

EXPECTED_SHA = '4cb3fa5c77eea973a2b62ca61873f071692694f4c9a1832507fe2c8c9ba582b4'

def inspect(source, out):
    data = source.read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SHA:
        raise ValueError('This reverse-engineered layout is verified only for the documented image SHA256')
    out.mkdir(parents=True, exist_ok=True)
    (out/'assets').mkdir(exist_ok=True)
    (out/'pages').mkdir(exist_ok=True)
    u32 = lambda o: struct.unpack_from('<I', data, o)[0]
    header = [u32(i) for i in range(0, 0x58, 4)]
    page_table, page_count = header[2:4]
    bg_table, bg_count = header[8:10]
    icon_table, icon_count = header[12:14]
    assert page_count == bg_count == 30 and icon_count == 569
    errors = []
    decoded_cache = {}

    def descriptor(offset):
        address,w,h,packed = struct.unpack_from('<IHHI', data, offset)
        return dict(table_offset=offset,address=address,width=w,height=h,
                    size=packed&0xffffff,format=packed>>24)

    def rgba(values, fmt, w, h):
        v = values.astype(np.uint32)
        if fmt == 2:
            # Linear alpha expansion is a preview approximation to controller blending.
            px = np.stack([((v>>8)&15)*17,((v>>4)&15)*17,(v&15)*17,(v>>12)*17],axis=-1)
        else:
            px = np.stack([(v>>11)*255//31,((v>>5)&63)*255//63,(v&31)*255//31,np.full_like(v,255)],axis=-1)
        return Image.fromarray(px.astype('uint8').reshape(h,w,4))

    def decode(d):
        key = (d['address'],d['width'],d['height'],d['size'],d['format'])
        if key in decoded_cache: return decoded_cache[key]
        p,w,h,n,f = key
        image = None
        if n == 0:
            d['status'] = 'empty_or_nonbitmap'
        elif not (0 < w <= 2048 and 0 < h <= 2048 and p+n <= len(data)):
            d['status'] = 'invalid_bounds'; errors.append(dict(descriptor=d.copy()))
        elif f in (0,1,2) and n == w*h*2:
            image = rgba(np.frombuffer(data,dtype='<u2',count=w*h,offset=p), f,w,h)
        elif f == 3 and data[p:p+2] == b'LT':
            try:
                hw,hh = struct.unpack_from('<HH',data,p+2)
                inner_size=u32(p+8)
                assert (hw,hh)==(w,h) and inner_size<=n
                assert n-inner_size<=1
                d['trailing_alignment_bytes']=data[p+inner_size:p+n].hex()
                chunks=data[p+6]; cursor=p+12+chunks*516; pieces=[]
                for ci in range(chunks):
                    table=p+12+ci*516
                    chunk_header=u32(table); length=chunk_header&0xffffff; mode=chunk_header>>24
                    assert cursor+length<=p+inner_size
                    palette=np.frombuffer(data,dtype='<u2',count=256,offset=table+4)
                    content=np.frombuffer(data,dtype='u1',count=length,offset=cursor)
                    if mode==1:
                        assert length%2==0
                        runs=content.reshape(-1,2)
                        indices=np.repeat(runs[:,1],runs[:,0].astype(np.uint16)+1)
                    elif mode==0: indices=content
                    else: raise ValueError(f'unknown LT mode {mode:#x}')
                    pieces.append(palette[indices]);cursor+=length
                values=np.concatenate(pieces)
                assert cursor==p+inner_size and len(values)==w*h, (len(values),w*h)
                image=rgba(values,1,w,h)
                d['compressed_chunks']=chunks
            except Exception as e:
                d['status']='compressed_decode_failed'; errors.append({'descriptor':d.copy(),'error':str(e)})
        else:
            d['status']='unsupported_format'; errors.append({'descriptor':d.copy()})
        if image is not None:
            name=f'assets/{p:08X}_{w}x{h}_f{f}.png'
            image.save(out/name)
            d.update(status='decoded',png=name)
        decoded_cache[key]=(image,d.get('png'),d['status'])
        return decoded_cache[key]

    def decode_and_attach(d):
        img,path,status=decode(d)
        d['status']=status
        if path: d['png']=path
        return img

    # The two contiguous tables contain 569 descriptors each; their independently
    # decoded menu artwork is English and Chinese, respectively.
    icons=[]
    for bank in range(2):
        rows=[]
        for i in range(icon_count):
            d=descriptor(icon_table+(bank*icon_count+i)*12)
            d.update(id=i,bank=bank);decode_and_attach(d);rows.append(d)
        icons.append(rows)
    backgrounds=[]
    for i in range(page_count):
        d=descriptor(bg_table+i*12);d['page']=i;decode_and_attach(d);backgrounds.append(d)

    animations=[]
    table,count=header[10:12]
    for group in range(count):
        frame_table,frame_count=struct.unpack_from('<II',data,table+group*8)
        frames=[]
        for frame in range(frame_count):
            o=frame_table+frame*16
            address,reserved,w,h,packed=struct.unpack_from('<IIHHI',data,o)
            d=dict(table_offset=o,address=address,reserved=reserved,width=w,height=h,
                   size=packed&0xffffff,format=packed>>24,frame=frame)
            decode_and_attach(d);frames.append(d)
        animations.append(dict(group=group,frame_table=frame_table,frames=frames))

    def records(p,n,family):
        end=p+n; result=[]
        while p<end:
            typ=struct.unpack_from('<H',data,p)[0]
            prefix=5 if family=='display' else 3
            length_byte=data[p+prefix-1]
            length=length_byte&0x7f
            if p+prefix+length>end: raise ValueError(f'Widget crosses block end at {p:#x}')
            payload=data[p+prefix:p+prefix+length]
            item=dict(offset=p,type=typ,length=length,length_byte=length_byte,payload=payload.hex())
            if family=='display':
                item['parameter_address']=struct.unpack_from('<H',data,p+2)[0]
                if typ==3 and length==14:
                    fields=struct.unpack('<7H',payload)
                    item.update(zip(['variable','x','y','first_icon','last_icon','min_value','max_value'],fields))
                elif typ==5 and length>=12:
                    item.update(zip(['variable','x','y','width','height','first_animation'],struct.unpack_from('<6H',payload)))
            else:
                item['base_type']=typ&0x3fff
                if len(payload)>=8:
                    x1,y1,x2,y2=struct.unpack_from('<4H',payload)
                    item['rectangle_candidate']=[x1,y1,x2,y2]
                    item['rectangle_valid']=0<=x1<x2<=320 and 0<=y1<y2<=480
                if (typ&0x3fff)==1 and length==16:
                    values=struct.unpack('<8H',payload)
                    item.update(zip(['x1','y1','x2','y2','return_value','unpressed_icon','pressed_icon','goto_page'],values))
            result.append(item);p+=prefix+length
        assert p==end
        return result

    pages=[]
    for i in range(page_count):
        dp,dn,tp,tn=struct.unpack_from('<IHIH',data,page_table+i*12)
        display=records(dp,dn,'display');touch=records(tp,tn,'touch')
        page=dict(id=i,display_offset=dp,display_size=dn,touch_offset=tp,touch_size=tn,
                  display=display,touch=touch,background=backgrounds[i])
        previews=[]
        for bank in range(2):
            img=Image.new('RGBA',(320,480),(0,0,0,255))
            omissions=collections.Counter()
            bg=decode_and_attach(backgrounds[i])
            if bg: img.alpha_composite(bg,(0,0))
            def paste_icon(icon,x,y):
                if icon==65535:return
                if not 0<=icon<icon_count: omissions['icon_id_out_of_range']+=1;return
                resource=icons[bank][icon]
                bitmap=decode_and_attach(resource)
                if bitmap is not None:img.alpha_composite(bitmap,(x,y))
                else:omissions['nonbitmap_icon']+=1
            for widget in display:
                if widget['type']==3:
                    paste_icon(widget['first_icon'],widget['x'],widget['y'])
                elif widget['type']==5 and widget['first_animation']<len(animations):
                    first=decode_and_attach(animations[widget['first_animation']]['frames'][0])
                    if first: img.alpha_composite(first,(widget['x'],widget['y']))
                    omissions['animation_first_frame_only']+=1
                else:omissions[f'display_type_{widget["type"]:04X}']+=1
            for widget in touch:
                if widget['base_type']==1 and widget['length']==16:
                    paste_icon(widget['unpressed_icon'],widget['x1'],widget['y1'])
            rel=f'pages/page_{i:02d}_bank{bank}.png';img.convert('RGB').save(out/rel)
            previews.append(dict(bank=bank,png=rel,omitted=dict(omissions)))
        page['previews']=previews;pages.append(page)

    # Additional flash regions are outside the first UI project. All operations
    # remain file reads: addresses below are offsets in this recovered image.
    project_size=u32(0x174)
    projects=[]
    for base in (0,0x05B10000,0x065455EC,0x06F7ABD8):
        blob=data[base:base+project_size]
        assert u32(base+0x174)==project_size and len(blob)==project_size
        projects.append(dict(base=base,size=project_size,end=base+project_size,
            sha256=hashlib.sha256(blob).hexdigest(),
            header_80=data[base+0x80:base+0x90].hex(),
            widgets_equal_first=data[base+0x11dd0:base+0x251a5]==data[0x11dd0:0x251a5]))

    def crc16(blob):
        table=[]
        for i in range(256):
            c=i
            for _ in range(8):c=(c>>1)^0xa001 if c&1 else c>>1
            table.append(c)
        c=0xffff
        for v in blob:c=(c>>8)^table[(c^v)&255]
        return c

    user_images=[]
    for base in (0x04000000,0x04060000,0x040C0000,0x041E0000):
        n,w,h=struct.unpack_from('<IHH',data,base)
        stored=struct.unpack_from('<H',data,base+9)[0]
        actual=crc16(data[base+11:base+11+n])
        d=dict(header_offset=base,address=base+11,width=w,height=h,size=n,
               format=1,stored_crc16=stored,computed_crc16=actual,crc_matches=stored==actual)
        assert (w,h,n)==(320,480,307200)
        decode_and_attach(d);user_images.append(d)
    base=0x04240000
    payload_size=u32(base+4);frame_count=data[base+13];frames=[]
    assert frame_count==171 and u32(base)==frame_count*20
    for i in range(frame_count):
        off=base+i*20
        relative,total,w,h,fmt,count,reserved,delay,crc=struct.unpack_from('<IIHHBBHHH',data,off)
        assert (total,count)==(payload_size,frame_count)
        address=base+relative
        d=dict(frame=i,table_offset=off,address=address,width=w,height=h,format=fmt,
               size=u32(address+8),delay_raw=delay,stored_crc16=crc)
        decode_and_attach(d);frames.append(d)
    gif_start=base+frame_count*20;gif_end=gif_start+payload_size
    assert frames[-1]['address']+frames[-1]['size']==gif_end
    actual=crc16(data[gif_start:gif_end]);stored=frames[0]['stored_crc16']
    user_animation=dict(base=base,payload_size=payload_size,end=gif_end,frames=frames,
                        stored_crc16=stored,computed_crc16=actual,crc_matches=stored==actual)

    stats=dict(pages=len(pages),display_records=sum(len(p['display']) for p in pages),
               touch_records=sum(len(p['touch']) for p in pages),icon_descriptors=2*icon_count,
               unique_decoded_images=sum(im is not None for im,_,_ in decoded_cache.values()),
               animations=len(animations),animation_frames=sum(len(g['frames']) for g in animations),
               decode_issues=len(errors))
    manifest=dict(source='UartTFT-II_Flash.bin',sha256=digest,size=len(data),header_words=header,
                  stats=stats,pages=pages,icons=icons,animations=animations,decode_issues=errors,
                  projects=projects,user_images=user_images,user_animation=user_animation)
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'touch_zones.csv').open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.writer(f);writer.writerow(['page','offset','type','length','rectangle_candidate','return_value','goto_page','payload'])
        for p in pages:
            for t in p['touch']:
                writer.writerow([p['id'],f'0x{t["offset"]:08X}',f'0x{t["type"]:04X}',t['length'],t.get('rectangle_candidate'),
                                 f'0x{t["return_value"]:04X}' if 'return_value' in t else '',t.get('goto_page',''),t['payload']])
    sheet=Image.new('RGB',(6*180,5*290),'#151a22');draw=ImageDraw.Draw(sheet)
    for p in pages:
        x=(p['id']%6)*180;y=(p['id']//6)*290
        thumb=Image.open(out/p['previews'][0]['png']);thumb.thumbnail((170,255));sheet.paste(thumb,(x+5,y+25))
        draw.text((x+5,y+5),f'Page {p["id"]:02d} / {len(p["touch"])} zones',fill='white')
    sheet.save(out/'overview.jpg',quality=90)
    (out/'viewer_data.js').write_text('const MODEL='+json.dumps(manifest,ensure_ascii=False)+';',encoding='utf-8')
    print(json.dumps(stats,indent=2))

if __name__=='__main__':
    inspect(Path(sys.argv[1]),Path(sys.argv[2]))
