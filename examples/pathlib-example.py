import pathlib

#Creating a path object
input_path = pathlib.Path('C:/example_directory/example_item.txt')

#Getting only the file name; .stem is a str type
filename = input_path.stem # output : example_item.txt
filename_noext = input_path.name # output : example_item
ext = input_path.suffix # output : .txt

#Getting only the directory
directory_path = input_path.parent # output : C:/example_directory/

#Getting all files in a directory with specific pattern in filename
for file_path in directory_path.glob('*.txt'): 
    print(file_path)

#Joining paths; directory to file
new_path = directory_path.joinpath('new_example_item.txt')

#Checking for type
new_path.is_dir()
new_path.is_file()

