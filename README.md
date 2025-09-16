### Installation

#### install pretrained gpt model

The pre-trained model is too big to be uploaded (100 Mb) 

```sh
$ mv gpt.pt 3000/src/sft/.
```

#### set up `venv`

```sh
$ python3 -m venv .venv
$ source .venv/bin/activate
```

#### dev

```sh
$ pip install -e ".[dev]"
```

### Run

```sh
$ jupyter notebook
```
