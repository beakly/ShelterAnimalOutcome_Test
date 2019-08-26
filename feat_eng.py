import os
import platform
import pandas as pd

# filepath
mac_path = "/Users/rocket/projects/datarobot"
lin_path = "/home/luna/projects/datarobot"

subproj_path = "ShelterAnimalOutcome"

if platform.system() == "Darwin":
    proj_path = os.path.join(mac_path, subproj_path)
elif platform.system() == "Linux":
    proj_path = os.path.join(lin_path, subproj_path)

read = "Data/train.csv"
write = "Data/train2.csv"
file_path = os.path.join(proj_path, read)
write_path = os.path.join(proj_path, write)

# read data
data = pd.read_csv(file_path)
data.columns

# set index
data = data.set_index('AnimalID')

# splitting age upon outcome and pivoting based on number + period
print(data['AgeuponOutcome'].unique())
age = data['AgeuponOutcome'].str.split(" ", n=1, expand=True)
age.dropna(inplace=True)
age[1] = age[1].replace(
    {"year": "years", "month": "months", "week": "weeks", "day": "days"}
    )
age_pivot = age.pivot(columns=1, values=0).fillna(0)
cols = age_pivot.columns[age_pivot.dtypes.eq('object')]
age_pivot[cols] = age_pivot[cols].apply(
    pd.to_numeric, errors='coerce', axis=1
    )

# forming new age data in months
age_pivot['age_months'] = (age_pivot.days / 30) \
    + (age_pivot.months) + (age_pivot.weeks / 4) \
    + (age_pivot.years * 12)

# merge to data set
data = pd.merge(
    left=data, right=age_pivot['age_months'],
    left_index=True, right_index=True,
    validate='1:1')
data = data.drop('AgeuponOutcome', axis=1)

# set feature for pure vs mixed breeds
data['Breed'] = data['Breed'].str.lower()
data['Pure'] = 'Yes'
data.loc[data['Breed'].str.contains(r'mix|/', regex=True), 'Pure'] = 'No'

# write out
data.to_csv(write_path)
