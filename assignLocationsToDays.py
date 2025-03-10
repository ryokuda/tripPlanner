import json
import math
import numpy as np
import parameters

# Binary tree package
class TreeNode:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None
        self.t = 0
        self.in_t = None  # DFS開始時刻
        self.out_t = None  # DFS終了時刻

    @staticmethod
    def assign_dfs_times(root):

        def _dfs_assign_times(root, node):
            if node is None:
                return
            root.t += 1
            node.in_t = root.t  # 入り時間を記録
            _dfs_assign_times(root, node.left)
            _dfs_assign_times(root, node.right)
            root.t += 1
            node.out_t = root.t  # 出る時間を記録

        root.t = 0  # 初期化
        _dfs_assign_times( root, root )

    @staticmethod
    def select_valid_nodes(root, num_days):
        """
        二分木を探索し、valid=True のノードをスコア順にソートし、先祖・子孫関係を考慮しながら4つのノードを選択する。
        :param root: 二分木のルートノード
        :return: 選択された4つのノードのリスト
        """

        def get_all_valid_nodes(node):
            """ 再帰的に valid=True のノードを収集 """
            if node is None:
                return []
            nodes = get_all_valid_nodes(node.left) + get_all_valid_nodes(node.right)
            if node.valid:
                nodes.append(node)
            return nodes

        def is_ancestor(ancestor, descendant):
            """ ancestor が descendant の先祖であるか判定 (DFS の in_t, out_t を利用) """
            return ancestor.in_t < descendant.in_t and ancestor.out_t > descendant.out_t

        def custom_sort(nodes):
            """ スコアの降順に並べた後、スコアが同じノードは先祖が前に来るようにする """
            nodes.sort(key=lambda n: n.score, reverse=True)  # まずスコアで降順ソート

            # 先祖が前に来るように安定ソート
            for i in range(len(nodes)):
                for j in range(i + 1, len(nodes)):
                    if nodes[i].score == nodes[j].score and is_ancestor(nodes[j], nodes[i]):
                        # i が j の子孫なら順番を入れ替える
                        nodes[i], nodes[j] = nodes[j], nodes[i]

            return nodes

        def find_common_ancestors(node_a, node_b, selected):
            """ node_a と node_b の共通の先祖を selected の中から探す """
            return {c for c in selected if is_ancestor(c, node_a) and is_ancestor(c, node_b)}

        # 1. valid=True のノードをすべて取得し、score の降順でソート
        valid_nodes = get_all_valid_nodes(root)
        valid_nodes = custom_sort(valid_nodes)

        if not valid_nodes:
            return []  # valid=True のノードが1つもない場合

        # 2. 最もスコアが高いノードを選択し、初期化
        selected = {valid_nodes[0]}  # 選択済みのノード
        candidate = set()  # 親子関係のあるノードを格納する候補

        # 3. valid_nodes を順に見て、selected に追加
        for i in range(1, len(valid_nodes)):

            if len(selected) >= num_days:
                break  # num_daysつのノードを選んだら終了

            node = valid_nodes[i]

            # 先祖が selected に存在するかチェック
            if not any(is_ancestor(ancestor, node) for ancestor in selected):
                #print( f'{i}:added to selected')
                #print( is_ancestor( valid_nodes[1],valid_nodes[0]))
                selected.add(node)  # 直接 selected に追加
            else:
                candidate.add(node)  # 親子関係があるなら候補に追加

                # 4. candidate から共通の先祖を削除する
                found = False  # 二重ループを抜けるフラグ
                for a in list(candidate):
                    for b in list(candidate):
                        if a != b and not is_ancestor(a, b) and not is_ancestor(b, a):
                            # A, B に共通の先祖が selected 内にあるか
                            common_ancestors = find_common_ancestors(a, b, selected)

                            if common_ancestors:
                                # 共通の先祖を selected から削除
                                selected -= common_ancestors
                                # A, B を selected に追加
                                selected.add(a)
                                selected.add(b)
                                # A, B を candidate から削除
                                candidate.remove(a)
                                candidate.remove(b)
                                found = True  # 二重ループを抜けるためのフラグ
                                break  # 内側のループを抜ける
                    if found:
                        break  # 外側のループを抜ける

        return list(selected)

    def get_leaf_nodes(self):
        """このノードのサブツリーに含まれる全てのリーフノードをリストとして返す"""
        if self.left is None and self.right is None:
            return [self]  # 自身がリーフならリストに追加
        leaves = []
        if self.left:
            leaves.extend(self.left.get_leaf_nodes())
        if self.right:
            leaves.extend(self.right.get_leaf_nodes())
        return leaves

class Location(TreeNode):
    def __init__(self, latitude, longitude, location_id=0, name="", score=0, category="", time=1.0, range=0.0, valid=False, left=None, right=None):
        super().__init__((latitude, longitude))  # ツリーノードの値として (latitude, longitude) を使用
        self.location_id = int(location_id)
        self.name = name
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.category = category
        self.score = int(score)
        self.time = time
        self.range = range
        self.valid = valid
        self.left = left
        self.right = right

    def distance( self, other_loc ):
        """
        100km以下の距離に限定し、平面近似で2地点間の距離を計算する。
        :param latitude1: 地点1の緯度（度）
        :param longitude1: 地点1の経度（度）
        :param latitude2: 地点2の緯度（度）
        :param longitude2: 地点2の経度（度）
        :return: 2地点間の距離（km）
        """
        # 地球の平均半径（km）
        R = 6371.0

        # 緯度・経度の差をラジアンに変換
        lat1, lon1 = math.radians(self.latitude), math.radians(self.longitude)
        lat2, lon2 = math.radians(other_loc.latitude), math.radians(other_loc.longitude)

        dlat = lat2 - lat1
        dlon = (lon2 - lon1) * math.cos(lat1)  # 高緯度での距離縮小を考慮

        # 近似的な平面距離計算（ピタゴラス定理）
        distance = R * math.sqrt(dlat ** 2 + dlon ** 2)

        return distance

    @staticmethod
    def merge(loc1, loc2):
        """ 2つのLocationインスタンスを統合し、新しいLocationを生成 """

        def get_leaf_scores(node):
            """ 再帰的にリーフノードのスコアを収集する """
            if node is None:
                return []
            if node.left is None and node.right is None:
                return [node.score]
            return get_leaf_scores(node.left) + get_leaf_scores(node.right)

        def get_leaf_times(node):
            """ 再帰的にリーフノードのtimeを収集する """
            if node is None:
                return []
            if node.left is None and node.right is None:
                return [node.time]
            return get_leaf_times(node.left) + get_leaf_times(node.right)

        def get_leaf_locations(node):
            """ 再帰的にリーフノードの位置情報を収集する """
            if node is None:
                return []
            if node.left is None and node.right is None:
                return [node]
            return get_leaf_locations(node.left) + get_leaf_locations(node.right)

        # リーフノードのスコアを取得
        leaf_scores = get_leaf_scores(loc1) + get_leaf_scores(loc2)
        leaf_scores.sort(reverse=True)
        top_3_scores = leaf_scores[:3] + [0] * (3 - len(leaf_scores))
        new_score = sum(top_3_scores) // 3  # 整数除算

        # リーフノードのtimeを取得し合計
        leaf_times = get_leaf_times(loc1) + get_leaf_times(loc2)
        new_time = sum(leaf_times)

        # 新しいLocationオブジェクトの位置を決定
        new_latitude = (loc1.latitude + loc2.latitude) / 2
        new_longitude = (loc1.longitude + loc2.longitude) / 2

        # リーフノードとの距離の最大値をrangeとする
        leaf_locations = get_leaf_locations(loc1) + get_leaf_locations(loc2)
        new_range = max(node.distance(Location(new_latitude, new_longitude)) for node in leaf_locations)

        # valid の決定条件、Locationが存在する範囲（存在する円の半径）がDISTANCE_THよりも小さい
        new_valid = new_range <= parameters.DISTANCE_TH # and new_time >= parameters.TIME_TH

        return Location(latitude=new_latitude, longitude=new_longitude, score=new_score, time=new_time, range=new_range,
                        valid=new_valid, left=loc1, right=loc2)

def cluster_locations(locations):
    """
    地点をクラスタリングして二分木を構築する
    :param locations: 初期のLocationインスタンスのリスト
    :return: クラスタリング後のルートノード
    """
    # 初期の集合 L
    L = locations[:]

    # 初期の距離行列を作成
    N = len(L)
    distances = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j:
                distances[i][j] = L[i].distance(L[j])

    while len(L) > 1:
        # 最小距離の2点を探す
        min_i, min_j = np.unravel_index(np.argmin(distances + np.eye(len(L)) * 1e10), distances.shape)

        # 最も近い2つの地点を取得
        loc1, loc2 = L[min_i], L[min_j]

        # 新しいクラスタを作成
        new_loc = Location.merge(loc1, loc2)

        # 古い地点を L から削除
        del L[max(min_i, min_j)]  # インデックスが大きい方を先に削除
        del L[min(min_i, min_j)]

        # 新しい地点を L に追加
        L.append(new_loc)

        # 距離行列を更新
        new_distances = np.zeros((len(L), len(L)))
        for i in range(len(L) - 1):
            new_distances[i, -1] = new_distances[-1, i] = L[i].distance(new_loc)
        distances = new_distances

    return L[0]  # 最終的なルートノードを返す


def load_locations(location_filename, scores_filename):
    with open(location_filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    print( f'    load location list from "{location_filename}"')

    with open(scores_filename, 'r', encoding='utf-8') as file:
        scores = json.load(file)
    print( f'    load location score from "{scores_filename}"')

    # location_id をキーにしたスコア辞書を作成
    score_map = {int(s["location_id"]): int(s["score"]) for s in scores}

    seen = set()
    locations = []

    for item in data:
        location_id = int(item["location_id"])
        category = item["category"].get("name","")
        score = score_map.get(location_id,0)
        if score > 50 and category != "restaurant" and location_id not in seen:
            seen.add(location_id)
            locations.append(Location(
                location_id=location_id,
                name=item["name"],
                latitude=float(item["latitude"]),
                longitude=float(item["longitude"]),
                category=item["category"].get("name",""),
                score=score  # スコアがない場合は0を設定
            ))
    return locations

def assignLocationsToDays():
    print( "" )
    print( "------ Step 4: Assign locations to eah day ------")
    # 全ロケーションの情報とスコア値を読み込む
    locations = load_locations(parameters.run_dir+"4.locationDetails.json", parameters.run_dir+"5.locationScores.json")

    # 距離が近いロケーションをマージして２分木を生成する
    root = cluster_locations( locations )

    # 2分木のノードの先祖/子孫の判断を高速に行うためのデータを付ける
    TreeNode.assign_dfs_times( root )

    # 2分木を、num_days個のサブツリーに分ける。各々が１日で訪問するLocationを示す
    selected_nodes = TreeNode.select_valid_nodes(root, num_days=parameters.NUM_DAYS )

    #print("Selected Nodes:")
    #for node in selected_nodes:
    #    print(f"Location range: {node.range}, Time: {node.time}, Score: {node.score}")

    # num_days個のサブツリーのリーフノードのLocationを取得して２重リストにする
    selectedLocations=[]
    for node in selected_nodes:
        leaf_nodes = node.get_leaf_nodes()
        leaf_nodes.sort(key=lambda x: x.score, reverse=True )
        selectedLocations.append(leaf_nodes)

    # 各日程の先頭5カ所のLocationを取得する
    max_locations=parameters.TIME_TH
    locationCandidates = [ sublist[:max_locations] for sublist in selectedLocations ]

    dailyLocations = []
    for i, day in enumerate(locationCandidates):
        print( f"Day{i+1}:" )
        onedayLocations = []
        for item in day:
            onedayLocations.append( {
                "location_id": item.location_id,
                "name": item.name,
                "latLong": f"{item.latitude},{item.longitude}",
                "score": item.score,
            })
            print( f'    location_id: {item.location_id}: name: {item.name} ')
        dailyLocations.append( onedayLocations )

    #print( dailyLocations )
    with open(parameters.run_dir+"6.dailyLocations.json", "w", encoding="utf-8") as f:
        json.dump(dailyLocations, f, indent=4, ensure_ascii=False)

    return dailyLocations

if __name__ == "__main__":
    assignLocationsToDays()