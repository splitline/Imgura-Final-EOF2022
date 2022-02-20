import asyncio
import json
import aiohttp
import random
import secrets
import os
import glob
import mimetypes

images = None
if os.getenv('TEST_MODE') == 'True':
    images = glob.glob('./images/*')
else:
    images = glob.glob('/manager/scripts/images/*')

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.34",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.43",
    "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36 Edg/96.0.1054.29",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 Edg/95.0.1020.44",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36 Edg/96.0.1054.41",
    "Mozilla/5.0 (Windows NT 10.0; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 OPR/80.0.4170.63",
    "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:95.0) Gecko/20100101 Firefox/95.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36 OPR/81.0.4196.61",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:96.0) Gecko/20100101 Firefox/96.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36",
    "curl/7.77.0",
    "curl/7.78.0",
    "curl/7.79.0",
    "curl/7.80.0",
    "curl/7.81.0",
    "sqlmap/1.6.1.7#dev (https://sqlmap.org)",
    "sqlmap/1.6.1.6#dev (https://sqlmap.org)",
    "sqlmap/1.6.1.5#dev (https://sqlmap.org)",
    "sqlmap/1.6.1.4#dev (https://sqlmap.org)",
    "python-requests/2.24.0"
]

image_urls = ["https://i.imgur.com/e8aQOzY.png","https://i.imgur.com/dghX7XT.png","https://i.imgur.com/3kI2Cmx.png","https://i.imgur.com/NLkFgEB.png","https://i.imgur.com/baxos4P.png","https://i.imgur.com/Spj2f5I.png","https://i.imgur.com/2qM1RQB.png","https://i.imgur.com/5WkR8qb.png","https://i.imgur.com/inOQkQs.png","https://i.imgur.com/5D5NnVY.png","https://i.imgur.com/MwkLDIS.png","https://i.imgur.com/vJHfNNA.png","https://i.imgur.com/FbgjZ7U.png","https://i.imgur.com/7di0Fb0.png","https://i.imgur.com/fvBagcE.png","https://i.imgur.com/UblLRn9.png","https://i.imgur.com/Nedoztc.png","https://i.imgur.com/uQ6U0X3.png","https://i.imgur.com/5LdIrd0.png","https://i.imgur.com/jAU2zm4.png","https://i.imgur.com/dhoRHZi.png","https://i.imgur.com/SI8OvXc.png","https://i.imgur.com/Nj7TgsM.png"]

image_url_contents = [b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xc8\x00\x00\x00\xc8\x08\x06\x00\x00\x00\xadX\xae\x9e\x00\x00 \x00IDATx\x9cL\xbb\xd7\x8f$i\xba\xdeW"x(\x80\x17\xba\x10\x04\x88\x80 ]H\xd0\x85D\t\x04\x04JZ\x92\xc7\xee\xd9\xd9={\xc6\xf7L\xcf\xb4\xab\xaa\xae\xae.\xef+\xcb\xa5\xf7>lfDF', b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00P\x00\x00\x00P\x08\x06\x00\x00\x00\x8e\x11\xf2\xad\x00\x00 \x00IDATx\x9c\xcc\xbcy\xb8eU}\xe7\xfdYk\xed\xf1\xcc\xc3\x9d\xc7\x9ag(\xa0@@D@\x91(\x93\x11\x81\xe0\x18\t4\xa4\xbb\xd3\xfa\xb6\xb1\xdb\x84'O\xa8\xca`:\xddi\x13\x87\x97\x0e\x98\x90\xc4", b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00 \x00IDATx\x9c\xec\xbd\xdb\xaf/Y\x92\xdf\xf5\x89\xb5V\xe6\xef\xf7\xdb\xb7s\xads\xeaTUO\xf7\xb8\xc7\x1e\xdf\xc7 \x98\x01a$\xb0\x85\xc4\x8b\xb1`x@\x02\x8c\xc4\x03\x12\x12\x7f\x00/<\xc0+\x0f\x96', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\xc8\x00\x00\x00\xc8\x08\x06\x00\x00\x00\xadX\xae\x9e\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04sBIT\x08\x08\x08\x08|\x08d\x88\x00\x00 \x00IDATx\x9c\xec\xbdy\xb4%Uy\xf0\xfd\xdbSU\x9d\xe1\x0e=\xd0\xdd\xcc\xa0\x18b\x12MLP\x12%', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00tVIDATx\xda\xbc}\x07\x80%gq\xe6\xd7\xfdr\x9e7or\x8e\xbb\xb39(\xecj\x15P\x00\x89 0B"\x993p\xd8\x8016\xc6\xf6\x1dg\xc0g\xaf\x0f\x8c1&\x1eg\x8c1\x871\x08\x8c\xc8', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00p\x00\x00\x00p\x08\x06\x00\x00\x00\xc6\xe0\xf4K\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00 cHRM\x00\x00z&\x00\x00\x80\x84\x00\x00\xfa\x00\x00\x00\x80\xe8\x00\x00u0\x00\x00\xea`\x00\x00:\x98\x00\x00', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00k\x08\x06\x00\x00\x00\xbf\xbd\x8a\x8a\x00\x00\x01\x06iCCPICC Profile\x00\x00x\x9cc``\x92`\x00\x02\x16\x03\x06\x86\xdc\xbc\x92\xa2 w\'\x85\x88\xc8(\x05\x06$\x90\x98\\\\\xc0\x80\x1b020|\xbb\x06"\x19\x18.\xeb\xe2', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00w\x08IDATx\xda\xec\xbd\x07x\\g\x996|\x9f3}\xa4Q\x1du\xc9\xb2\xe4"\xd7\xd8ql\xa7:\xbd\x90@\x02\x84\xc0B\x08\x016$Y\xc2B\x96\xb2,|\xb4@h\xa1o\x96\xc0~\xb4eS\x80\x14', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00l\x08\x06\x00\x00\x00\xa2\xb8\xba2\x00\x00t{IDATx\x9c\xec\xbdex\\\xd7\xd5\xbf}\xefs\xce\xb0\x98\xc1\x96,\xb0d\xcb\xccl9\xe6\xd8\x0eG\x0e3S\xdb$m\xd2\x86\x145m\ni\x98\xda`\x1bjc\x05\x1d\xb6\x1dC\xcc\xcc\xcc\x96,\xc6', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00u\x00\x00\x00\x80\x08\x06\x00\x00\x005[&\x16\x00\x00x\x93IDATx\x9c\xac\xfdw\x9c\xa6\xc7u\xdf\x89~+<\xe1\xcdo\xe7\x9e\x9e\x9c\x032@\x00$\x00&P\x0c\xa22eR\x96tm\xcb\xf2\xee\xf5\xdaw\xd7\xf7\xda\xab\xf5~\xf6\xfa\xda\x10\xe4\xf4\xf1z\xbd\x0e', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00\x01\x85iCCPICC Profile\x00\x00x\x9c}\x91=H\xc3@\x18\x86\xdf\xa6J\xa5TD\xed \xe2\x90\xa1:Y\x10\x15q\x94*\x16\xc1Bi+\xb4\xea`r\xe9\x1f4iHR\\\x1c\x05', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00{+IDATx\x9c\xec\xfdw\xbc]U\x9d\xff\x8f?\xd7\xda\xed\xf4\xdb\xfb\xbd\xe9=!\x1d\x12j\x08M\x90"(\xc1\xae\xd8@A\xc7\xae\xa3\xe3L\xc42:\xea\xd8\xb0\xb7\x11\xc1F\x14\x90&M\xc8\xa5C\x08\xa4', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00|\x08\x02\x00\x00\x00.\x0c/\xfe\x00\x00Y\xb5IDATx\x01d\xc1M\x8f\xb5\xd9y\x1d\xe6\xb5\xd6\xbd\xf7sNU\xbd\x9f\xdddK\x96(\x91\xb2\xe5\x18\x08\x0c\xc3\xf3\x00\xf9=\xc9,\xf3\xfc\xc0\xcc<\n<Pb\x05A,\xb1\x9bM\xb2\xbb\xdf\xfa8\xe7', b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00 \x00IDATx\x9cL\xbc\xd9\xafl\xd9}\xdf\xf7Y\xe3\x9ej<\xd3\x9d\xfbv7\xd9\x1cE5iI$\xa2\xc8\x89`\xc8\x8e\xad\xb7\x00\t\x90?'\x7fD\x90\xbc\xe5", b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00oMIDATx\x9c\xad\xfdy\xb4}[v\xd7\x87}\xe6Zk\xef}\x9a\xdb\xfc\xfa\xdf{\xbf\xd7V\xa3R\xa9\xaa$$\x10\x88\x1e\xd1y\x0c\xba\xe0\x0c\xa22\x01\x9cA @\x06\xc1!d\x84\xe0\xc4\x98Wrl', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00z\xfdIDATx\xda\xec\xbd\x07\x98%Wu.\xba\xaa\xce9\x9ds\xce9N\xceI#\xcdH#\xa1\x9c\x85%\xa2M\xe6b\xebb\x0c6\xf7\x1ald_\x1b\x0706&<\x036\x18\xc9"\x08\x8c%\x94P\x18', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00}\x00\x00\x00\x80\x08\x06\x00\x00\x00&\x8cf\xe2\x00\x00a\xd0IDATx\x9c\xed\xfdy\xd0u\xd9u\xde\x87\xfd\xd6\x1e\xce9\xf7\xbe\xc37\xf6\xd7\x8d\x06\xd9\x04E\x90\x80\t\x98\x14%\xda\xa4H\x89"LJEA\t\xad\xc4\xe9\xb6\xe4De\xbb\xca\xa9\xb8$\x97e%\xd1', b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00j\x96IDATx\x9ce\xfdW\xb3lI\x92\xa5\x89}jdo'\x87]\x16<2\x8btUVu\xa1{\xa4\x00<\x00\xbf\x02\xff\x19\x10\x01\x06\x02\x91\x11\x01\xa6iNu%\x8d\x0cz\xd9!N\xf663\xc5\x83", b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00p\x00\x00\x00p\x08\x06\x00\x00\x00\xc6\xe0\xf4K\x00\x00 \x00IDATx\x9c\xec\xbdy\xf4l\xd7U\xdf\xf9\xd9\xe7\x9c{oU\xfd\xe67O\xd2{z\x92,Y\x9e\x00;!6\xc1\x0e\x83\xc9\x04\x04B#\x13:\x0c\x81t\xe8\x04\x08\xe9\xd8\x81t \x18\x03NV\x00w', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00Y\x00\x00\x00Y\x08\x06\x00\x00\x00U\x0b\x88\xaf\x00\x00\x00\x01sRGB\x00\xae\xce\x1c\xe9\x00\x00\x00\x04gAMA\x00\x00\xb1\x8f\x0b\xfca\x05\x00\x003:IDATx^\xed}\x07|\\\xd5\x95\xbe\xd9\x14\xba)\x7f\x02!@ \xc1,\x81\x90\x05\xc2\x86l \x90d', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00t\x00\x00\x00\x80\x08\x06\x00\x00\x00\xda\x99M(\x00\x00l\x91IDATx\x9c\xd5\xfdw\x9c]\xd7Y\xef\x8f\xbf\xd7n\xa7\xb7\xe9]3\xa3\xde\xac\xe6"w\xc9\x8e\x1d\x97\x98\xc4I\xa4\x84\x14\xb8\xb4\x1b.\x97o\xb8\x90\x00\x97{\x01I\x94P\x02\\:8\x81\x04\xd2\x91H', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x80\x00\x00\x00\x80\x08\x06\x00\x00\x00\xc3>a\xcb\x00\x00c\xb3IDATx\x9c\xe5\xbdy\x9ce\xd7U\xdf\xfb\xdd{\x9f\xe9N5W\xf5\xdc\x92\xba\xd5\x1alY\xb2\x06\xcb\x96,\x0f\xd8\xd8\x10c\x83\r\x96\x08S\x1ef\x86@\x02\t\xc9\xcb\xcb\xd4R\x98\x1c\xc2\xe3\x11\x9c|', b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00(\x00\x00\x00(\x08\x06\x00\x00\x00\x8c\xfe\xb8m\x00\x00\x10/IDATX\x85E\x98\xd9\x8be\xd7y\xc5\x7f\xe7\x9c}\xc6;\xdf[U]cOR\xab[\x92%\xdbhh\x05#;/\x1e\xb01$\xc4\x10;6\xc9\x1f\x90\x17?\x84\xfc\x1f\xc1O\x01;\x81<8/y']

# Image related checker
async def check_image(base_url, session, nanoid, orig_image):
    try:
        extension = os.path.splitext(orig_image)[1]
        response = await session.get(url=base_url+'/uploads/'+nanoid+extension)
        if response.status != 200:
            return False
        
        if orig_image.startswith('https://'):
            img_index = image_urls.index(orig_image)
            orig_content= image_url_contents[img_index]
            content = await response.content.read(100)
            if content != orig_content:
                return False
            return True

        # first 100 bytes of image
        with open(orig_image, 'rb') as f:
            content = await response.content.read(100)
            if f.read(100) != content:
                return False
        return True
    except Exception as e:
        return False

async def check_view(base_url, session, nanoid, orig_image):
    try:
        extension = os.path.splitext(orig_image)[1]
        response = await session.get(url=base_url+'/view/'+nanoid)
        if response.status != 200:
            return False
        resp = await response.text()
        if "/uploads/"+nanoid+extension not in resp or "<strong>Image ID:</strong> "+nanoid not in resp:
            return False
        return True
    except Exception as e:
        return False

async def check_api(base_url, session, nanoid, orig_image):
    try:
        extension = os.path.splitext(orig_image)[1]
        response = await session.post(base_url+'/api/image_info', json={'image': f"uploads/{nanoid}{extension}"})
        if response.status != 200:
            return False

        resp = await response.json()
        if orig_image.startswith('https://'):
            if resp['mime'].split('/')[0] != 'image' or not resp['size']:
                return False
            return True

        mime = mimetypes.guess_type(orig_image)
        if resp['mime'] != mime[0] or resp['size'] != os.path.getsize(orig_image):
            return False
        return True
    except Exception as e:
        print(e)
        return False


async def check_upload_by_url(base_url, session, cookies):
    try:
        upload_image = random.choice(image_urls)
        response = await session.post(
            url=base_url+'/upload',
            cookies=cookies,
            data={'url': upload_image},
            allow_redirects=False)
        if response.status != 302:
            return False

        loc = response.headers['Location']
        if not loc.startswith(base_url+'/view/'):
            print(loc)
            return False
        nanoid = loc.split("/")[-1]
        if len(nanoid) != 8:
            return False

        res = await asyncio.gather(
            check_image(base_url, session, nanoid, upload_image),
            check_view(base_url, session, nanoid, upload_image),
            check_api(base_url, session, nanoid, upload_image)
        )
        return all(res)
    except Exception as e:
        print(e)
        return False



# Web related checker
async def check_user(base_url, session):
    try:
        user, pwd = ("test"+secrets.token_hex(8),
                    secrets.token_urlsafe(random.randint(10, 20)))
        data = {
            'username': user,
            'password': pwd,
        }
        # print(data)
        url = base_url + '/login?redirect=/'
        response = await session.post(url=url, data=data, allow_redirects=False)
        cookie = response.cookies
        if response.status != 302:
            return False
        resp = await response.text()
        if f'<html><head><meta http-equiv="refresh" content="0;url={response.headers["Location"]}"></head></html>' not in resp or\
                response.headers['Location'] != base_url+'/':
            return False
        upload_image = random.choice(images)
        response = await session.post(
            url=base_url+'/upload',
            allow_redirects=False,
            cookies=response.cookies,
            data={"image": open(upload_image, 'rb')})
        if response.status != 302:
            return False
        loc = response.headers['Location']
        if not loc.startswith(base_url+'/view/'):
            return False
        nanoid = loc.split("/")[-1]
        if len(nanoid) != 8:
            return False

        res = await asyncio.gather(
            check_image(base_url, session, nanoid, upload_image),
            check_view(base_url, session, nanoid, upload_image),
            check_api(base_url, session, nanoid, upload_image),
            check_upload_by_url(base_url, session, cookie)
        )
        return all(res)
    except Exception as e:
        print(e)
        return False


async def check_login_page(base_url, session):
    redir = secrets.token_urlsafe(random.randint(1, 10))
    url = base_url + '/login?redirect=' + redir
    try:
        response = await session.get(url=url)
        if response.status == 200:
            resp = await response.text()
            if f'<form action="/login?redirect={redir}" method="post">' in resp and \
                    'Login / Register' in resp and 'placeholder="Your Username"' in resp:
                return True
            return False
        else:
            return False
    except Exception as e:
        print(e)
        return False

async def check_admin(base_url, session):
    try:
        response = await session.post(url=base_url+'/login', data={'username': 'admin', 'password': 'VU5KmCL8l0CAFuJfb1s3dbwaPWq8Fm9akdRF4qJ34Q0'}, allow_redirects=False)
        response = await session.get(url=base_url+'/admin', cookies=response.cookies)
        if response.status != 200:
            return False
        resp = await response.text()
        # print(resp)
        if 'Admin Panel</h1><br>' not in resp or \
             '<form action="/admin/backup" method="post">' not in resp \
                 or '<form action="/admin/give-admin" method="post">' not in resp:
            return False
        return True
    except Exception as e:
        print(e)
        return False

# init
async def checker(base_url):
    async with aiohttp.ClientSession(
        headers={
            "User-Agent": random.choice(user_agents),
            #"Host": "chals2.eof.ais3.org:" + base_url.split(":")[-1]
        },
        timeout=aiohttp.ClientTimeout(connect=1, sock_read=4)
    ) as session:
        ret = await asyncio.gather(
            check_login_page(base_url, session),
            check_user(base_url, session),
            check_admin(base_url, session),
        )
        if not all(ret):
            return False
        return True


async def check_all(urls):
    ret = await asyncio.gather(*[checker(url) for url in urls])
    return ret


if __name__ == '__main__':
    import sys
    team_id = int(sys.argv[1])
    print(asyncio.run(check_all([
        f'http://127.0.0.1:{30000+team_id}',
    ])))

