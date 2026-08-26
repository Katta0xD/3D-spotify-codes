# 3D-spotify-codes
Tool to create different 3D models of Spotify barcodes ready to print
<img width="619" height="180" alt="image" src="https://github.com/user-attachments/assets/66fe2fa9-5ef9-4fe2-b7f8-5f6eb7d0d263" />
<img width="953" height="370" alt="image" src="https://github.com/user-attachments/assets/ada2f401-891b-4cd6-82d4-e96962987c2a" />

## How to use 
### clone this repo and move in
```bash
git clone https://github.com/Katta0xD/3D-spotify-codes && cd 3D-spotify-codes
```

### Create a virtual environment to install dependencies
```bash
mkdir venv && python -m venv venv
```
activate the virtual environment
```bash
source venv/bin/activate
```
install the dependencies
```bash
pip install --prefer-binary -r requirements.txt
```

### Config
rename config.txt.template as config.txt
```bash
mv config.txt.template config.txt
```
use your favorite text editor to edit the file and specify a path to save the .stl files after ```Save Path=```

### execute the program
```bash
python3 gui.py
```
or
```bash
chmod +x ./gui.py
./gui.py
```
