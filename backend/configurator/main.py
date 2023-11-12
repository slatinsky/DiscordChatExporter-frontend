import pymongo

URI = "mongodb://127.0.0.1:27017"
client = pymongo.MongoClient(URI)
db = client["dcef"]
collection_guilds = db["guilds"]
collection_config = db["config"]

def pad_id(id):
	if id == None:
		return None
	return str(id).zfill(24)

def get_guilds():
    return collection_guilds.find().sort("msg_count", pymongo.DESCENDING)

def get_allowlisted_guild_ids():
	allowlisted_guild_ids = collection_config.find_one({"key": "allowlisted_guild_ids"})["value"]
	allowlisted_guild_ids = [pad_id(id) for id in allowlisted_guild_ids]
	return allowlisted_guild_ids

def get_denylisted_user_ids():
    denylisted_user_ids = collection_config.find_one({"key": "denylisted_user_ids"})["value"]
    denylisted_user_ids = [pad_id(id) for id in denylisted_user_ids]
    return denylisted_user_ids

def set_allowlisted_guild_ids(allowlisted_guild_ids):
    print("Applying allowlisted guild ids...")
    collection_config.update_one({"key": "allowlisted_guild_ids"}, {"$set": {"value": allowlisted_guild_ids}})
    if len(allowlisted_guild_ids) == 0:
        print("all guilds are now allowlisted")
    else:
        print(f"allowlisted {len(allowlisted_guild_ids)} guilds")
    print("")

def set_denylisted_user_ids(denylisted_user_ids):
    print("Applying denylisted user ids...")
    collection_config.update_one({"key": "denylisted_user_ids"}, {"$set": {"value": denylisted_user_ids}})
    if len(denylisted_user_ids) == 0:
        print("no users are denylisted")
    else:
        print(f"{len(denylisted_user_ids)} users are now denylisted")

def resolve_user_id(user_id):
    user_id = pad_id(user_id)
    guilds = list(get_guilds())
    for guild in guilds:
        authors_collection_name = f"g{pad_id(guild['_id'])}_authors"
        authors_collection = db[authors_collection_name]

        user = authors_collection.find_one({"_id": user_id})
        if user != None:
            return user['names'] + user['nicknames']

def menu_allowlist():
    guilds = list(get_guilds())
    allowlisted_ids = get_allowlisted_guild_ids()
    allowlisted_ids = [id for id in allowlisted_ids if id in [guild['_id'] for guild in guilds]]  # remove invalid ids
    while True:
        print("choice | action           | allowlist status | guild_name")
        print("-------|------------------|------------------|--------------------------")
        print("CTRL+C | back             | -                | -                        ")
        for i, guild in enumerate(guilds):
            is_allowlisted = guild['_id'] in allowlisted_ids
            allowlisted_status = ""
            if is_allowlisted:
                allowlisted_status = "allowlisted    "
            elif len(allowlisted_ids) == 0:
                allowlisted_status = "not-configured "
            else:
                allowlisted_status = "not-allowlisted"
            print(f"{str(i).ljust(6)} | toggle allowlist | {allowlisted_status}  | {guild['name']}")
        try:
            index = int(input(f"Index of guild to toggle allowlist status (0-{len(guilds)-1}): "))
            guild_id = guilds[index]['_id']
            if guild_id in allowlisted_ids:
                allowlisted_ids.remove(guild_id)
            else:
                allowlisted_ids.append(guild_id)

            set_allowlisted_guild_ids(allowlisted_ids)

        except ValueError:
            print("Invalid input")
            break

        except KeyboardInterrupt:
            print("\nExiting...")
            break

def menu_add_user_to_denylist(denylisted_user_ids):
    while True:
        try:
            print("\n(right click profile picture in DCEF -> Copy author ID)")
            user_id = input("User id: ")
            user_id = pad_id(user_id)
            user_names = resolve_user_id(user_id)
            if user_names == None:
                print("User not found")
                continue

            print("Found user:", ', '.join(user_names))
            if user_id in denylisted_user_ids:
                print("This user is already denylisted")
                continue

            denylisted_user_ids.append(user_id)
            set_denylisted_user_ids(denylisted_user_ids)
            break

        except KeyboardInterrupt:
            print("\nExiting...")
            break

    return denylisted_user_ids


def menu_denylist_users():
    denylisted_user_ids = list(get_denylisted_user_ids())

    while True:
        print("")
        print("choice | action                | user_id                  | also_known_as")
        print("-------|-----------------------|--------------------------|--------------------------")
        print("CTRL+C | back                  | -                        | -                        ")
        print("0      | hide new user         | -                        | -                        ")
        for i, user_id in enumerate(denylisted_user_ids):
            print(f"{str(i+1).ljust(5)}  | remove from denylist  | {user_id} | {', '.join(resolve_user_id(user_id))}")
        try:
            index = int(input(f"Choice (0-{len(denylisted_user_ids)}): "))
            if index == 0:
                denylisted_user_ids = menu_add_user_to_denylist(denylisted_user_ids)
            else:
                user_id = denylisted_user_ids[index-1]
                denylisted_user_ids.remove(user_id)
                set_denylisted_user_ids(denylisted_user_ids)
                continue


        except ValueError:
            print("Invalid input")
            break

        except KeyboardInterrupt:
            print("\nExiting...")
            break

def main():
    print("\n")
    print("############################")
    print("# DCEF server configurator #")
    print("############################")
    print("(all changes are applied immediately)\n")

    print("Connecting to mongo database (DCEF needs to be running)...")
    try:
        client.server_info()
        print("Database is online\n")
    except:
        print("Database is offline. Run DCEF and try again\n")
        return



    while True:
        print("choice | action")
        print("-------|-----------------")
        print("CTRL+C | exit            ")
        print("0      | Show/hide servers")
        print("1      | Hide users  ")
        print("")
        try:
            choice = int(input("Choice (0-1): "))
            if choice == 0:
                menu_allowlist()
            elif choice == 1:
                menu_denylist_users()
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid choice")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()