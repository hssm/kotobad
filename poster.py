from atproto import Client, models

entries = []
client = Client()
client.login('', '')

def load_data():
    with open("wordlist.txt", "r") as f:
        current = ""
        for line in f:
            if line.startswith("---BEGIN"):
                continue
            if line.startswith("---END"):
                entries.append(current)
                current = ""
                continue
            current += line

def post_next():
    with open('index', 'r') as f:
        index = int(f.read())

    index += 1
    post_body = entries[index].strip()
    post = client.send_post(post_body)
    parent = models.create_strong_ref(post)

    client.send_post(
        text='reply post',
        reply_to=models.AppBskyFeedPost.ReplyRef(parent=parent, root=parent)
    )

    with open("index", "w+") as f:
        f.write(str(index))


if __name__ == "__main__":
    load_data()
    post_next()
