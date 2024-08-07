# CHUNITHM Tool Analysis
Use **Requsts** and **bs4** get player socre

And Show it in **flask** web
## Main Concept
1. Get player Score and song const base rating caluate rating 
1. Show Chart ladar to show weak and Strength
1. Show Table to show your socre
1. Show Chart your rating change history
1. Show Chart your play count and time
1. Display Same Team song recommand
1. Random Select song by diffcult 
1. And update Add to favoriate
## File Structure
```
CHUNITHM_Tool
├── main.py
├── templates
│   ├── score.html
│   ├── table.html
└── requirements.txt
└── readme.md
```
## Boot up
```
pip install -r requirements.txt
python main.py
```
Your Can Open it in your broswer
#### Done
1. Login(
2. Get Const Rating of song
3. Save history song socre
4. Login Fail Handle
#### Progress
1. Song Display filter and sort by name or const rating
#### To Do
1. Prettiy Display Web
2. Player History Raing Chart by diffcult
3. Player History rating change chart