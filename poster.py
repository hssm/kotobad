from atproto import Client, models

entries = []
client = Client()
client.login('', '')

def load_data():
    with open("wordlist.txt", "r") as f:
        post = [""]
        reply = [""]
        current = post
        for line in f:
            if line.startswith("---BEGIN"):
                post[0] = ""
                reply[0] = ""
                current = post
                continue
            if line.startswith("---REPLY"):
                current = reply
                continue
            if line.startswith("---END"):
                entries.append((post[0], reply[0]))
                current = None
                continue
            if current:
                current[0] += line

def post_next():
    with open('index', 'r') as f:
        index = int(f.read())

    index += 1
    post_body, reply_body = entries[index]
    post = client.send_post(post_body)
    if len(reply_body) > 0:
        parent = models.create_strong_ref(post)
        client.send_post(
            text=reply_body,
            reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent, root=parent)
        )

    with open("index", "w+") as f:
        f.write(str(index))


if __name__ == "__main__":
    load_data()
    post_next()
