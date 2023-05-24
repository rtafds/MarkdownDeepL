import json
import deepl
import argparse
import re

def load_settings():
    global master_data, translator
    # デフォルト値

    master_data = {
        "auth_key": "",
        "source_lang": "EN",
        "target_lang": "JA"
    }
    try:
        with open("config.json") as fp:
            update_data = json.load(fp)
        for k, v in update_data.items():
            master_data[k] = v
    except Exception as e:
        pass


def translate(source_string):
    # Get Replacement rule
    #rules_path = f"rules/{master_data['source_lang']}_{master_data['target_lang']}.txt"
    #replacement_rule = []
    #if os.path.exists(rules_path):
    #    with open(rules_path, "r") as fp:
    #        rules_raw = fp.readlines()
    #    for rule in rules_raw:
    #        tmp_split = rule.replace("\n", "").split("\t")
    #        if(len(tmp_split)) >= 2:
    #            replacement_rule.append([tmp_split[0], tmp_split[1]])

    # split contents
    sources, tmp = [], []
    cnt = 0
    for s in source_string.splitlines(keepends=True):
        cnt += len(s)
        if cnt > 4500:
            sources.append("".join(tmp))
            tmp = [s]
            cnt = len(s)
        else:
            tmp.append(s)
    else:
        sources.append("".join(tmp))

    # DeepL Translate
    try:
        translator = deepl.Translator(auth_key=master_data["auth_key"])
        result = translator.translate_text(
                    [sources], 
                    source_lang=master_data["source_lang"],
                    target_lang=master_data["target_lang"],
                    tag_handling="xml",
                    ignore_tags=["keep","keep2"])
        usage = translator.get_usage()
        result_txt = "\n".join([r.text for r in result])
    except Exception as ex:
        return "", "DeepL translation error\n"+str(ex)

    # ルールベースで置き換え
    message = ""
    #for rule in replacement_rule:
    #    try:
    #        #print(rule)
    #        result_txt = re.sub(rule[0], rule[1], result_txt)
    #    except Exception as ex:
    #        message = f"Replacement rule error at {rule[0]} -> {rule[1]}\n"+str(ex)
    #
    if message == "":
        return result_txt, f"Translate success\nCharacter usage: {usage.character.count} of {usage.character.limit}"
    else:
        return result_txt, message
    

def read_markdown(path):
    lines = []
    load_str = ''
    with open(f"{path}", encoding="utf-8") as f:
        lines = f.readlines()    # mdファイルの内容を1行ずつ配列に入れる
    load_str = ''.join(lines)    # 全行を取得後、配列を結合して文字列変数に入れ    
    return load_str


def tex_perserve_preprocess(load_str):
    # $aa$びように挟まれた場所を翻訳されないように、<keep>aaa</keep>で挟む。
    # いいやり方を思いつかなかったので、交互に変換する。ちゃんと交互になっていると信じる。
    for i in range(10000):
        load_str = load_str.replace(r"$",r"<keep>",1)
        load_str = load_str.replace(r"$",r"</keep>",1)
    # $$aa$$の場合は、<keep></keep>になってしまっているので、そこは<keep2>aaa</keep2>に変える。
    for i in range(1000):
        load_str = load_str.replace(r"<keep></keep>",r"<keep2>",1)
        load_str = load_str.replace(r"<keep></keep>",r"</keep2>",1)
    return load_str

def to_notion_tex_postprocess(result_str):
    result_str = re.sub(r"<keep>",r" \$\$", result_str)
    result_str = re.sub(r"</keep>", r"\$ ", result_str)
    result_str = re.sub(r"<keep2>", r"$$\n\\begin{align*}", result_str)
    result_str = re.sub(r"</keep2>", r"\\end{align*}\n$$", result_str)
    return result_str


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # ②コマンドライン引数の定義をadd_argument()で追加
    #   位置引数 ('-'無しの名前を指定する。定義した順で一つ目・二つ目...と扱われる)
    parser.add_argument("input_dir")
    parser.add_argument("output_dir")
    #   オプション引数 ('-'有りの名前を指定する。順不同)
    parser.add_argument("--middle_dir", default=None)
    #parser.add_argument("--opt2")

    # ③コマンドライン引数解析を実行 (デフォルトで処理されるのでargvとかの指定は不要)
    args = parser.parse_args()
    
    input_dir = args.input_dir
    output_dir = args.output_dir
    middle_dir = args.middle_dir
    
    # 設定の読み込み。config.jsonの auto_key にちゃんとDeepLのAPIキーを設定する。
    load_settings()
    
    # ファイルの読み込み
    load_str = read_markdown(input_dir)
    
    # texが翻訳されないように、保護するための前処理
    load_str = tex_perserve_preprocess(load_str)
    # 前処理結果を見たい時
    if middle_dir is not None:
        with open(f"{middle_dir}", mode="w") as f:
            f.write(load_str)
    
    # 翻訳にぶち込む
    result_txt, message = translate(load_str)
    print(message)  # DeepLの残り翻訳数やエラー等の表示
    
    # notionで数式がいい感じになるように後処理
    result_str = to_notion_tex_postprocess(result_txt)
    with open(f"{output_dir}", mode="w") as f:
        f.write(result_str)