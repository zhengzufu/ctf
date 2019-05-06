# INS'hAck 2019

[ https://ctftime.org/event/763 ]

## Passthru

> You're part of a company security team and the admin has recently enabled interception on the company filtering proxy. The admin is pretty confident when it comes to its domain whitelist. He gave you a [capture](https://static.ctf.insecurity-insa.fr/13140c280d45224949bfe7fc1b978c6b97ddd55d.tar.gz) to review. Time to prove him wrong.

[ **forensics** : 206pts ]

Extracting and then unzipping `passthru.zip` from the given [download](https://static.ctf.insecurity-insa.fr/13140c280d45224949bfe7fc1b978c6b97ddd55d.tar.gz), gives the following two files:

```
capture.pcap            
sslkey.log  
```

Inspecting `capture.pcap` in `wireshark` required setting the `(PRE)-Master-Secret log filename` to point at `sslkey.log` in order to view the `TLS` data.

After spending a while examining the decrypted packet data, the only thing that seemed to call for a closer investigation was the URL mentioned in repeated `GET` requests to [images.google.com](https://images.google.com/):

```
GET /searchbyimage?image_url=http%3A%2F%2Frequestbin.net%2Fr%2Fzk2s2ezk%3Fid%3D82290383-7480-487c-b78b-77ac769c56cd%26kcahsni%3D9ef773fe97f56554a3b4&encoded_image=&image_content=&filename=&hl=fr HTTP/1.1 
```

Decoding the `image_url` querystring parameter makes it a little easier to read:

```
http://requestbin.net/r/zk2s2ezk?id=82290383-7480-487c-b78b-77ac769c56cd&kcahsni=9ef773fe97f56554a3b4
```

Visiting the image URL and a deeper look into [requestbin.net](http://requestbin.net/) uncovered nothing special; however, the use of the parameter `kcahsni` in the URL, which spells `inshack` (the name of the CTF) backwards, suggested looking further and it soon became obvious that the hex characters following `kcahsni` changed for each subsequent `GET` request. Concatenating these values together to see if they revealed the flag was the logical next step.

The following commands extract all the querystring parameters into a file called `queries.txt` (the `editcap` command was only necessary as `tshark` kept erroring because the original `pcap` file had truncated the final packet):

```
editcap -r capture.pcap fixed.pcap 1-5438
tshark -r fixed.pcap -o 'ssl.keylog_file:sslkey.log' -Y 'http contains "GET /searchbyimage"' -T fields -e http.request.uri.query.parameter > queries.txt
```

And the script below then extracts and concatenates all the `kcahsni` hex values before decoding them.

```
hexstr = ''
with open('queries.txt', 'rt') as f:
    hexstr = ''.join([param.split(',')[0][109:] for param in f.readlines()])

out = bytes.fromhex(hexstr).decode('latin1')
print(out)
```

The output wasn't pretty, but the flag is relatively obvious.

```
÷sþõeT£´&Íá÷óÜî¯rZ¹9hüRð<
}e59ad3f38a01dca00f9759e6d205317642c5421fcdad034ebe7077c2bddd472b{ASNI2ÃÐl$ò¨ÇèfgÛ÷þÎ(EjÒJÂÆ¡.>þK
```

A little string slicing and reversing, `print(out[102:32:-1])`, then cleans up the flag:

```
INSA{b274dddb2c7707ebe430dadcf1245c246713502d6e9579f00acd10a83f3da95e}
```
