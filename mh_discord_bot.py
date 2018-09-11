import discord
import sqlite3


#discord code
TOKEN = 'NDM5NTc5MDE4OTMzNTY3NDkz.DcVN2Q.dbQas-EwIggCWRQDkOreu2rld9g'

client = discord.Client()

@client.event
async def on_message(message):
    #do not reply to yourself
    if message.author == client.user:
        return

    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        print(message.author)
        await client.send_message(message.channel, msg)

    #MH Testing
    if message.content.startswith('fleets=') or message.content.startswith('Fleets='):

        #make strings
        content = str(message.content)
        author = str(message.author)

        #parse content
        fleet_input = content.split('=')[1].split(',')

        #connect to the db
        con = sqlite3.connect('damage_list.db')
        cur = con.cursor()

        #search for author records
        cur.execute("SELECT * FROM damage WHERE player LIKE (?)", (author,))
        record = cur.fetchall()

        #if not found add player
        if len(record) < 1:
            print('Not Found')
            cur.execute("INSERT INTO damage(player) VALUES (?)", (author,))

        #if found, modify
        else:
            print('Found')

        for index, fp in enumerate(fleet_input):

            fleet_num = 'fleet_'+str(index+1)
            sql_command = "UPDATE damage SET " + fleet_num + " = " + fp + " WHERE player = '" + author + "'"
            cur.execute(sql_command)

        #write changes
        con.commit()

        #close db
        con.close()

        #update discord
        msg = 'Fleet records have been saved for {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('?fleets') or message.content.startswith('?Fleets'):

        author = str(message.author)

        con = sqlite3.connect('damage_list.db')
        cur = con.cursor()

        #search for author records
        cur.execute("SELECT * FROM damage WHERE player LIKE (?)", (author,))
        record = cur.fetchall()

        if len(record) > 0:
            print(record[0])
            msg = '{0.author.mention}: {1}, {2}, {3}, {4}, {5}, {6}, {7}, {8}, {9}, {10}' \
                  ''.format(message, record[0][1], record[0][2], record[0][3], record[0][4], record[0][5],
                            record[0][6], record[0][7], record[0][8], record[0][9], record[0][10])
            await client.send_message(message.channel, msg)
        else:
            msg = "{0.author.mention}'s fleets were not found".format(message)
            await client.send_message(message.channel, msg)

        con.close()

    if message.content.startswith('op=') or message.content.startswith('Op='):

        author = str(message.author)
        content = str(message.content)

        con = sqlite3.connect('damage_list.db')
        cur = con.cursor()

        #search for author records
        cur.execute("SELECT * FROM damage WHERE player LIKE (?)", (author,))
        record = cur.fetchall()

        if len(record) < 1:

            msg = "{0.author.mention}'s fleets were not found".format(message)
            await client.send_message(message.channel, msg)

        else:

            #get info from message
            boosts, full_health = content.split('=')[1].split(',')
            boosts = int(boosts)
            full_health = float(full_health)
            print('-------------')
            print('{}'.format(author))
            print('Boosts: {} Full Op Health: {}'.format(boosts, full_health))

            #op=boosts,op full health
            #RAW DAMAGE PER FLEET
            #=fleet fp*(1+0.1*boosts)
            #boosted fleet damage
            boosted_fleets = []
            for fleet in record[0]:
                #ignore author
                if type(fleet) != type(''):
                    #build boosted fleet dmg list
                    boosted_fleets.append(fleet*(1+0.1*boosts))
            print('Boosted Fleets: {}'.format(boosted_fleets))

            #CAP
            #total op hp / 20
            #calculate cap
            cap = full_health / 20
            print('Damage Cap: {}'.format(cap))

            #CAP check per fleet
            #if raw fleet damage is > cap, only do the capped damage
            capped_fleets = []
            for boosted_fleet in boosted_fleets:
                if boosted_fleet > cap:
                    capped_fleets.append(cap)
                else:
                    capped_fleets.append(boosted_fleet)
            print("Capped Fleets: {}".format(capped_fleets))

            #TOTAL DAMAGE IN MILL
            #the sum of all fleets capped damage
            total_damage_mill = sum(capped_fleets)
            print("Total Damage (Millions): {}".format(total_damage_mill))

            #TOTAL DAMAGE IN %
            #total damage in mill/total op hp*100
            total_damage_percentage = total_damage_mill / full_health * 100
            print('Total Damage %: {0:.2f}%'.format(total_damage_percentage))
            #send to discord
            msg = "{0.author.mention}  {1:.2f}%".format(message, total_damage_percentage)
            await client.send_message(message.channel, msg)

        con.close()


    if message.content.startswith('boosts=') or message.content.startswith('Boosts='):

        content = str(message.content)
        author = str(message.author)
        #boosts = int(message.content)
        boosts = content.split('=')[1]
        print(boosts)

        #connect to the db
        con = sqlite3.connect('damage_list.db')
        cur = con.cursor()

        #search for author records
        cur.execute("SELECT * FROM damage WHERE player LIKE (?)", (author,))
        record = cur.fetchall()

        if len(record) > 0:
            sql_command = "UPDATE damage SET boosts = " + boosts + " WHERE player = '" + author + "'"
            cur.execute(sql_command)
        else:
            msg = "{0.author.mention}'s fleets were not found".format(message)
            await client.send_message(message.channel, msg)

        #write changes
        con.commit()

        #close db
        con.close()

        #update discord
        msg = 'Boost records have been saved for {0.author.mention}'.format(message)
        await client.send_message(message.channel, msg)

    if message.content.startswith('?boosts') or message.content.startswith('?Boosts='):

        author = str(message.author)

        con = sqlite3.connect('damage_list.db')
        cur = con.cursor()

        #search for author records
        cur.execute("SELECT * FROM damage WHERE player LIKE (?)", (author,))
        record = cur.fetchall()



@client.event
async def on_ready():
    print('Logged In As')
    print(client.user.name)
    print(client.user.id)
    print('---------------')

client.run(TOKEN)