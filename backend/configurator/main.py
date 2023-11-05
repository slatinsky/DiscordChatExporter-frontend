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

def get_whitelisted_guild_ids():
	whitelisted_guild_ids = collection_config.find_one({"key": "whitelisted_guild_ids"})["value"]
	whitelisted_guild_ids = [pad_id(id) for id in whitelisted_guild_ids]
	return whitelisted_guild_ids

def get_blacklisted_user_ids():
    blacklisted_user_ids = collection_config.find_one({"key": "blacklisted_user_ids"})["value"]
    blacklisted_user_ids = [pad_id(id) for id in blacklisted_user_ids]
    return blacklisted_user_ids

def set_whitelisted_guild_ids(whitelisted_guild_ids):
    print("Applying whitelisted guild ids...")
    collection_config.update_one({"key": "whitelisted_guild_ids"}, {"$set": {"value": whitelisted_guild_ids}})
    if len(whitelisted_guild_ids) == 0:
        print("all guilds are now whitelisted")
    else:
        print(f"whitelisted {len(whitelisted_guild_ids)} guilds")
    print("")

def set_blacklisted_user_ids(blacklisted_user_ids):
    print("Applying blacklisted user ids...")
    collection_config.update_one({"key": "blacklisted_user_ids"}, {"$set": {"value": blacklisted_user_ids}})
    if len(blacklisted_user_ids) == 0:
        print("no users are blacklisted")
    else:
        print(f"{len(blacklisted_user_ids)} users are now blacklisted")

def resolve_user_id(user_id):
    user_id = pad_id(user_id)
    guilds = list(get_guilds())
    for guild in guilds:
        authors_collection_name = f"g{pad_id(guild['_id'])}_authors"
        authors_collection = db[authors_collection_name]

        user = authors_collection.find_one({"_id": user_id})
        if user != None:
            return user['names'] + user['nicknames']

def menu_whitelist():
    guilds = list(get_guilds())
    whitelisted_ids = get_whitelisted_guild_ids()
    whitelisted_ids = [id for id in whitelisted_ids if id in [guild['_id'] for guild in guilds]]  # remove invalid ids
    while True:
        print("choice | action           | whitelist status | guild_name")
        print("-------|------------------|------------------|--------------------------")
        print("CTRL+C | back             | -                | -                        ")
        for i, guild in enumerate(guilds):
            is_whitelisted = guild['_id'] in whitelisted_ids
            whitelisted_status = ""
            if is_whitelisted:
                whitelisted_status = "whitelisted    "
            elif len(whitelisted_ids) == 0:
                whitelisted_status = "not-configured "
            else:
                whitelisted_status = "not-whitelisted"
            print(f"{str(i).ljust(6)} | toggle whitelist | {whitelisted_status}  | {guild['name']}")
        try:
            index = int(input(f"Index of guild to toggle whitelist status (0-{len(guilds)-1}): "))
            guild_id = guilds[index]['_id']
            if guild_id in whitelisted_ids:
                whitelisted_ids.remove(guild_id)
            else:
                whitelisted_ids.append(guild_id)

            set_whitelisted_guild_ids(whitelisted_ids)

        except ValueError:
            print("Invalid input")
            break

        except KeyboardInterrupt:
            print("\nExiting...")
            break

def menu_add_user_to_blacklist(blacklisted_user_ids):
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
            if user_id in blacklisted_user_ids:
                print("This user is already blacklisted")
                continue

            blacklisted_user_ids.append(user_id)
            set_blacklisted_user_ids(blacklisted_user_ids)
            break

        except KeyboardInterrupt:
            print("\nExiting...")
            break

    return blacklisted_user_ids


def menu_blacklist_users():
    blacklisted_user_ids = list(get_blacklisted_user_ids())

    while True:
        print("")
        print("choice | action                | user_id                  | also_known_as")
        print("-------|-----------------------|--------------------------|--------------------------")
        print("CTRL+C | back                  | -                        | -                        ")
        print("0      | blacklist new user    | -                        | -                        ")
        for i, user_id in enumerate(blacklisted_user_ids):
            print(f"{str(i+1).ljust(5)}  | remove from blacklist | {user_id} | {', '.join(resolve_user_id(user_id))}")
        try:
            index = int(input(f"Choice (0-{len(blacklisted_user_ids)}): "))
            if index == 0:
                blacklisted_user_ids = menu_add_user_to_blacklist(blacklisted_user_ids)
            else:
                user_id = blacklisted_user_ids[index-1]
                blacklisted_user_ids.remove(user_id)
                set_blacklisted_user_ids(blacklisted_user_ids)
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
        print("0      | Whitelist server")
        print("1      | Blacklist user  ")
        print("")
        try:
            choice = int(input("Choice (0-1): "))
            if choice == 0:
                menu_whitelist()
            elif choice == 1:
                menu_blacklist_users()
            else:
                print("Invalid choice")
        except ValueError:
            print("Invalid choice")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()