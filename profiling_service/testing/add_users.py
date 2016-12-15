from profilingService import user_datastore, User

first = 'user'
last = 'doe'
for i in range(1000):
    if not User.objects(first_name=first + str(i).zfill(2), last_name=last + str(i).zfill(2)):
        user_datastore.create_user(first_name=first + str(i).zfill(2), last_name=last + str(i).zfill(2), email=first + str(i).zfill(2) + last + str(i).zfill(2) + '@gmail.com', password='spacegr', position=[35, 25])
    else:
        print('User already exists...')
