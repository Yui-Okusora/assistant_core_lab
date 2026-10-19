# assistant_monolith.py — "it works on my machine"
# Lab 3 starting point: a working but unmaintainable study-assistant script.
# DO NOT copy this style. Your job is to refactor it.
import csv, json, sys, time, random, os

API_KEY = "sk-test-2b7c1d9e4f0a"        # TODO move somewhere?
MODEL = "gpt-small"
RATE = 450000
RETAKE_RATE = 1.5
DEBUG = True
history = []
offices = {}
handbook = []
BASE = os.path.dirname(os.path.abspath(__file__))


def load():
    global offices, handbook
    try:
        f = open(BASE + "/data/offices.csv", encoding="utf-8")
        r = csv.reader(f)
        next(r)
        for row in r:
            offices[row[0].lower()] = row
        f.close()
    except:
        print("could not load offices")
    try:
        handbook = json.load(open(BASE + "/data/handbook.json", encoding="utf-8"))
    except:
        print("could not load handbook")


def llm(prompt):
    # pretend to call an LLM
    if DEBUG:
        print("[debug] calling", MODEL, "with key", API_KEY, "prompt:", prompt[:60])
    time.sleep(0.2)
    if random.random() < 0.1:
        raise Exception("LLM timeout")
    return "Here is what I found: " + prompt[-120:]


def handle(msg):
    global history
    history.append(msg)
    m = msg.lower().strip()
    if m == "":
        return "empty"
    if m in ["hi", "hello", "hey", "xin chao"]:
        return "Hello! I can help with offices, fees and rules."
    if m == "history":
        return "\n".join(history)
    if m == "stats":
        return stats()
    if m.startswith("save"):
        save_history(m.split()[-1] if len(m.split()) > 1 else "history.txt")
        return "saved"
    # fee question
    if "fee" in m or "tuition" in m:
        words = m.replace("?", " ").split()
        credits = 0
        retake = 0
        for i in range(len(words)):
            if words[i].isdigit():
                if i + 1 < len(words) and words[i + 1].startswith("retake"):
                    retake = int(words[i])
                elif credits == 0:
                    credits = int(words[i])
        if credits == 0:
            return "How many credits?"
        if credits > 30:
            return "too many credits"
        total = credits * RATE + retake * RATE * RETAKE_RATE
        return "Your tuition is " + str(int(total)) + " VND"
    # office question
    for k in offices:
        if k in m:
            o = offices[k]
            return o[0] + ": room " + o[1] + ", open " + o[2]
    # rule question -> search handbook then llm
    best = None
    best_score = 0
    for rule in handbook:
        score = 0
        for w in m.split():
            if len(w) > 3 and w in rule["text"].lower():
                score = score + 1
        if score > best_score:
            best_score = score
            best = rule
    if best != None and best_score >= 1:
        try:
            ans = llm("Answer using this rule: " + best["text"] + " Question: " + msg)
            return ans + " (source: " + best["id"] + ")"
        except Exception as e:
            print("error", e)
            return best["text"] + " (source: " + best["id"] + ")"
    return "Sorry I dont know"


def stats():
    # count what people ask about
    c = {"fee": 0, "office": 0, "rule": 0, "other": 0}
    for h in history:
        h = h.lower()
        if "fee" in h or "tuition" in h:
            c["fee"] += 1
        elif any(k in h for k in offices):
            c["office"] += 1
        elif any(w in h for w in ["thesis", "retake", "exam", "credit"]):
            c["rule"] += 1
        else:
            c["other"] += 1
    return "fee=" + str(c["fee"]) + " office=" + str(c["office"]) + " rule=" + str(c["rule"]) + " other=" + str(c["other"])


def save_history(fname):
    f = open(BASE + "/" + fname, "w")
    for h in history:
        f.write(h + "\n")
    f.close()
    if DEBUG:
        print("[debug] saved", len(history), "lines to", fname)


def main():
    load()
    if len(sys.argv) > 1:
        print(handle(" ".join(sys.argv[1:])))
        return
    print("assistant ready")
    while True:
        try:
            q = input("> ")
        except:
            break
        if q == "quit":
            break
        start = time.time()
        a = handle(q)
        print(a)
        if DEBUG:
            print("[debug] took", round(time.time() - start, 2), "s")


# some tests I run by hand
def test():
    load()
    print(handle("hi"))
    print(handle("tuition for 18 credits and 2 retake"))
    print(handle("where is the library"))
    print(handle("can I register my thesis with 118 credits"))
    print(handle("tuition 40 credits"))
    print(handle(""))


if __name__ == "__main__":
    if "--test" in sys.argv:
        sys.argv.remove("--test")
        test()
    else:
        main()
