# PlaidCTF 2019

[ https://ctftime.org/event/743 ]

## A Whaley Good Joke

> You'll have a whale of a time with [this one](https://play.plaidctf.com/files/pctf-whales_169aeb74f82dcdceb76e36a6c4c22a89)! I couldn't decide what I wanted the flag to be so I alternated adding and removing stuff in waves until I got something that looked good. Can you dive right in and tell me what was so punny?

Used `file` to determine that the given download contained `gzip compressed data` before extracting the contents using `tar`. This extracted a bunch of directories (each containing `layer.tar` and some other unimportant files), `44922ae2...c67ff784.json` and `manifest.json`.

I originally wrote some code to just decompress all the `layer.tar` files after discovering references to `/root/flag.sh` within `44922ae2...c67ff784.json`:

```json
{
  "container": "23e9240f8ca97d3bfba72f23a57703138fb3a16d7e3e19f7d5b80d177ab50b5d",
  "created": "2019-04-13T20:58:53.322050465Z",
  "os": "linux",
  "container_config": {
    "Tty": false,
    "Cmd": [
      "\/bin\/sh",
      "-c",
      "chmod +x .\/flag.sh && .\/flag.sh"
    ],
    "Volumes": null,
    "Domainname": "",
    "WorkingDir": "\/root\/",
  ...
}
```

Unfortunately, after extracting everything from each of the `layer.tar` files, running `flag.sh` resulted in a flag that was clearly not correct.

```
 $ ./flag.sh 
 pctf{1_b3tk4_auultn__s0lk3m7tr_ui2l7u_h_er}
```

A quick look at `flag.sh` shows that it concatenates 32 files (also within `/root`) that are named using the numbers 1 through 32 (with later examination revealing that each file contained a single character). The fact that the resulting flag was incorrect suggested files had been overwritten, and that the order of extraction was important.

```bash
#!/bin/bash

for i in {1..32}
do
    test -f $i
    if [[ $? -ne 0 ]]
    then
        echo "Missing file $i - no flag for you!"
        exit
    fi
done

echo pctf{1_b3t$(cat 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32)}
```

The `manifest.json` file (and also `44922ae2...c67ff784.json`) from the original archive confirm a particular extraction sequence for the `layer.tar` files, however, the names of **21** of the 27 directories extracted from the archive have been masked.

```json
{
  "Layers": [
    "2354d65e014cbe530f9695dbe3faf8ac84d85d7ad91f5d46ba8ef3fc0cd88d95\/layer.tar",
    "4337e82a87b98a9c74a8328f7059baf04a2ad31081c9893c5f37d4dd85137988\/layer.tar",
    "7204dd4cdfd9b6d29a095cf1fd3b2e7efe366f191c31a75df4ea8e9f47a70801\/layer.tar",
    "c843887778784dad565b239aa712a3228d9a878f2d3f129f3ab7341a84f11910\/layer.tar",
    "????????????????????????????????????????????????????????????????\/layer.tar",
    "????????????????????????????????????????????????????????????????\/layer.tar",
    "????????????????????????????????????????????????????????????????\/layer.tar",
    ...
    "????????????????????????????????????????????????????????????????\/layer.tar",
    "????????????????????????????????????????????????????????????????\/layer.tar",
    "????????????????????????????????????????????????????????????????\/layer.tar",
    "b94e5d83dbbff95e883f0f53bcf47c017471b13d81325697be6e22cdc8c369aa\/layer.tar",
    "24d12bbeb0a9fd321a8decc0c544f84bf1f6fc2fd69fa043602e012e3ee6558b\/layer.tar"
  ],
  ...
}
```

The `layer.tar` files from those particular directories also happened to specify only revisions that added or deleted different numbers and combinations of the 32 files comprising the flag within `/root`. This step did require some searching to discover that `.wh.` files are special **whiteout** files used by Docker to represent file and folder deletion.

Using the above knowledge and the clue within the challenge description about `alternated adding and removing stuff`, I eventually realised that it might be possible to determine the correct extraction order based on the following two principles:

* No file can be deleted that doesn't exist (ie, it must be added first)
* No file can be added that currently exists (ie, it must have *not* been added yet or needs to be deleted first)

My solution ([a-whaley-good-joke.py](a-whaley-good-joke.py)) creates a tree structure of alternating ADD/DELete revision nodes that explores sequence orders of revisions which satisfy the above rules. A valid sequence order will have a tree depth of 21 (ie, using all the possible revisions). The script then extracts the files based on each valid sequence ordering and displays the potential flag. 

There were actually 24 valid revision sequences combining for an assortment of possible flags:

```
Processing valid sequences ...
Extracting sequence #00 : pctf{1_b3tttzalkzgn_7s0lknq6___ui2l_u_h_er}
Extracting sequence #01 : pctf{1_b3tttzalkzgn_7s0lknq6___ui2l_u_h_er}
Extracting sequence #02 : pctf{1_b3tttzalkzgn_7s0lknq6___ui2l_u_h_er}
Extracting sequence #03 : pctf{1_b3tttzalkzgn_7s0lknq6___ui2l_u_h_er}
Extracting sequence #04 : pctf{1_b3t_u_couldnt_c0nt4in3r_ur_l4ught3r}
Extracting sequence #05 : pctf{1_b3t_u_couldnt0s0nt4in3e_urel4ught3r}
Extracting sequence #06 : pctf{1_b3t_u_couldnt0s0nt4in3e_urel4ught3r}
...
```

The correct result was determined by simply seeing which of the flags made sense.

```
pctf{1_b3t_u_couldnt_c0nt4in3r_ur_l4ught3r}
```
