import requests
import re
from collections import defaultdict
from datetime import datetime, timedelta

# -------------------------
# 频道分类（正规区域）
# -------------------------
CHANNEL_CATEGORIES = {
    "央视频道": ['CCTV1', 'CCTV2', 'CCTV3', 'CCTV4', 'CCTV4欧洲', 'CCTV4美洲', 'CCTV5', 'CCTV5+', 'CCTV6', 'CCTV7', 'CCTV8', 'CCTV9',
                 'CCTV10', 'CCTV11', 'CCTV12', 'CCTV13', 'CCTV14', 'CCTV15', 'CCTV16', 'CCTV17', '兵器科技', '风云音乐', '风云足球',
                 '风云剧场', '怀旧剧场', '第一剧场', '女性时尚', '世界地理', '央视台球', '高尔夫网球', '央视文化精品', '卫生健康', '电视指南'],
    "卫视频道": ['湖南卫视', '浙江卫视', '江苏卫视', '东方卫视', '深圳卫视', '北京卫视', '广东卫视', '广西卫视', '东南卫视', '海南卫视',
                 '河北卫视', '河南卫视', '湖北卫视', '江西卫视', '四川卫视', '重庆卫视', '贵州卫视', '云南卫视', '天津卫视', '安徽卫视',
                 '山东卫视', '辽宁卫视', '黑龙江卫视', '吉林卫视', '内蒙古卫视', '宁夏卫视', '山西卫视', '陕西卫视', '甘肃卫视',
                 '青海卫视', '新疆卫视', '西藏卫视', '三沙卫视', '厦门卫视', '兵团卫视', '延边卫视', '安多卫视', '康巴卫视', '农林卫视', '山东教育',
                 'CETV1', 'CETV2', 'CETV3', 'CETV4', '早期教育'],
    "数字频道": ['CHC动作电影', 'CHC家庭影院', 'CHC影迷电影', '淘电影', '淘精彩', '淘剧场', '淘4K', '淘娱乐', '淘Baby', '萌宠TV', '北京纪实科教', '重温经典',
                 '星空卫视', 'CHANNEL[V]', '凤凰中文', '凤凰资讯', '凤凰香港', '凤凰电影', '求索纪录', '求索科学', '求索生活', '求索动物',
                 '睛彩青少', '睛彩竞技', '睛彩篮球', '睛彩广场舞', '金鹰纪实', '快乐垂钓', '茶频道', '天元围棋', '魅力足球', '五星体育', '劲爆体育',
                 '乐游', '生活时尚', '都市剧场', '欢笑剧场', '游戏风云', '动漫秀场', '金色学堂', '法治天地', '哒啵赛事', '哒啵电竞', '黑莓电影', '黑莓动画', 
                 '卡酷少儿', '金鹰卡通', '优漫卡通', '哈哈炫动', '嘉佳卡通', 'iHOT爱喜剧', 'iHOT爱科幻', 'iHOT爱院线', 'iHOT爱悬疑',
                 'iHOT爱历史', 'iHOT爱谍战', 'iHOT爱旅行', 'iHOT爱幼教', 'iHOT爱玩具', 'iHOT爱体育', 'iHOT爱赛车', 'iHOT爱浪漫', 'iHOT爱奇谈',
                 'iHOT爱科学', 'iHOT爱动漫', '东北热剧', '中国功夫', '动作电影', '军事评论', '军旅剧场', '魅力潇湘',
                 '古装剧场', '家庭剧场', '惊悚悬疑', '明星大片', '欢乐剧场', '海外剧场', '潮妈辣婆', '爱情喜剧',
                 '炫舞未来', '精品体育', '精品大剧', '精品纪录', '精品萌宠', '超级体育', '超级电影', '怡伴健康',
                 '超级电视剧', '超级综艺', '金牌综艺', '武搏世界', '农业致富'],
}

# -------------------------
# 频道映射（别名 -> 规范名）
# -------------------------
CHANNEL_MAPPING = {
    "CCTV1": ["CCTV-1", "CCTV-1 HD", "CCTV-1 综合"],
    "CCTV2": ["CCTV-2", "CCTV-2 HD", "CCTV-2 财经"],
    "CCTV3": ["CCTV-3", "CCTV-3 HD", "CCTV-3 综艺"],
    "CCTV4": ["CCTV-4", "CCTV-4 HD", "CCTV4a", "CCTV4A", "CCTV-4 中文国际"],
    "CCTV4欧洲": ["CCTV-4欧洲", "CCTV-4欧洲 HD", "CCTV-4 欧洲", "CCTV4o", "CCTV4O", "CCTV-4 中文欧洲", "CCTV4中文欧洲"],
    "CCTV4美洲": ["CCTV-4美洲", "CCTV-4美洲 HD", "CCTV-4 美洲", "CCTV4m", "CCTV4M", "CCTV-4 中文美洲", "CCTV4中文美洲"],
    "CCTV5": ["CCTV-5", "CCTV-5 HD", "CCTV-5 体育"],
    "CCTV5+": ["CCTV-5+", "CCTV-5+ HD", "CCTV-5+ 体育赛事"],
    "CCTV6": ["CCTV-6", "CCTV-6 HD", "CCTV-6 电影"],
    "CCTV7": ["CCTV-7", "CCTV-7 HD", "CCTV-7 国防军事"],
    "CCTV8": ["CCTV-8", "CCTV-8 HD", "CCTV-8 电视剧"],
    "CCTV9": ["CCTV-9", "CCTV-9 HD", "CCTV-9 纪录"],
    "CCTV10": ["CCTV-10", "CCTV-10 HD", "CCTV-10 科教"],
    "CCTV11": ["CCTV-11", "CCTV-11 HD", "CCTV-11 戏曲"],
    "CCTV12": ["CCTV-12", "CCTV-12 HD", "CCTV-12 社会与法"],
    "CCTV13": ["CCTV-13", "CCTV-13 HD", "CCTV-13 新闻"],
    "CCTV14": ["CCTV-14", "CCTV-14 HD", "CCTV-14 少儿"],
    "CCTV15": ["CCTV-15", "CCTV-15 HD", "CCTV-15 音乐"],
    "CCTV16": ["CCTV-16", "CCTV-16 HD", "CCTV-16 奥林匹克", "CCTV16 4K", "CCTV16奥林匹克 4K"],
    "CCTV17": ["CCTV-17", "CCTV-17 HD", "CCTV-17 农业农村"],
    "兵器科技": ["CCTV-兵器科技", "CCTV兵器科技"],
    "风云音乐": ["CCTV-风云音乐", "CCTV风云音乐"],
    "第一剧场": ["CCTV-第一剧场", "CCTV第一剧场"],
    "风云足球": ["CCTV-风云足球", "CCTV风云足球"],
    "风云剧场": ["CCTV-风云剧场", "CCTV风云剧场"],
    "怀旧剧场": ["CCTV-怀旧剧场", "CCTV怀旧剧场"],
    "女性时尚": ["CCTV-女性时尚", "CCTV女性时尚"],
    "世界地理": ["CCTV-世界地理", "CCTV世界地理"],
    "央视台球": ["CCTV-央视台球", "CCTV央视台球"],
    "高尔夫网球": ["CCTV-高尔夫网球", "CCTV高尔夫网球", "CCTV央视高网", "CCTV-央视高网", "央视高网"],
    "央视文化精品": ["CCTV-央视文化精品", "CCTV央视文化精品", "CCTV文化精品", "CCTV-文化精品", "文化精品"],
    "卫生健康": ["CCTV-卫生健康", "CCTV卫生健康"],
    "电视指南": ["CCTV-电视指南", "CCTV电视指南"],
    "山东教育": ["山东教育卫视"],
    "CETV1": ["中国教育1台", "中国教育一台", "中国教育1", "CETV-1 综合教育", "CETV-1"],
    "CETV2": ["中国教育2台", "中国教育二台", "中国教育2", "CETV-2 空中课堂", "CETV-2"],
    "CETV3": ["中国教育3台", "中国教育三台", "中国教育3", "CETV-3 教育服务", "CETV-3"],
    "CETV4": ["中国教育4台", "中国教育四台", "中国教育4", "CETV-4 职业教育", "CETV-4"],
    "早期教育": ["中国教育5台", "中国教育5", "中国教育五台", "CETV早期教育", "CETV-早期教育", "CETV 早期教育", "CETV-5", "CETV5"],
    "CHC影迷电影": ["CHC高清电影", "chc影迷电影", "影迷电影", "chc高清电影"],
    "淘电影": ["IPTV淘电影", "北京IPTV淘电影", "北京淘电影"],
    "淘精彩": ["IPTV淘精彩", "北京IPTV淘精彩", "北京淘精彩"],
    "淘剧场": ["IPTV淘剧场", "北京IPTV淘剧场", "北京淘剧场"],
    "淘4K": ["IPTV淘4K", "北京IPTV淘4K", "北京淘4K", "北京IPTV4K超清", "淘 4K"],
    "淘娱乐": ["IPTV淘娱乐", "北京IPTV淘娱乐", "北京淘娱乐"],
    "淘Baby": ["IPTV淘BABY", "北京IPTV淘BABY", "北京淘BABY", "IPTV淘baby", "北京IPTV淘baby", "北京淘baby"],
    "萌宠TV": ["IPTV淘萌宠", "北京IPTV淘萌宠", "北京淘萌宠"],
    "求索纪录": ["求索记录", "求索纪录4K", "求索记录4K", "求索纪录 4K", "求索记录 4K"],
    "金鹰纪实": ["湖南金鹰纪实", "金鹰记实"],
    "北京纪实科教": ["纪实科教", "纪实科教8K"],
    "凤凰中文": ["凤凰卫视中文台", "凤凰中文台", "凤凰卫视中文"],
    "凤凰香港": ["凤凰卫视香港台", "凤凰卫视香港", "凤凰香港"],
    "凤凰资讯": ["凤凰卫视资讯台", "凤凰资讯台", "凤凰咨询", "凤凰咨询台", "凤凰卫视咨询台", "凤凰卫视资讯", "凤凰卫视咨询"],
    "凤凰电影": ["凤凰卫视电影台", "凤凰电影台", "凤凰卫视电影", "鳳凰衛視電影台", " 凤凰电影"],
    "乐游": ["乐游频道", "全纪实", "SiTV乐游", "SiTV乐游频道", "SiTV 乐游频道"],
    "欢笑剧场": ["欢笑剧场4K", "欢笑剧场 4K", "SiTV欢笑剧场", "SiTV 欢笑剧场"],
    "生活时尚": ["生活时尚4K", "SiTV生活时尚", "SiTV 生活时尚"],
    "都市剧场": ["都市剧场4K", "SiTV都市剧场", "SiTV 都市剧场"],
    "游戏风云": ["游戏风云4K", "SiTV游戏风云", "SiTV 游戏风云"],
    "金色学堂": ["金色学堂4K", "SiTV金色学堂", "SiTV 金色学堂"],
    "动漫秀场": ["动漫秀场4K", "SiTV动漫秀场", "SiTV 动漫秀场"],
    "卡酷少儿": ["北京卡酷", "卡酷卡通", "北京卡酷少儿", "卡酷动画"],
    "哈哈炫动": ["炫动卡通", "上海哈哈炫动"],
    "iHOT爱喜剧": ["iHOT 爱喜剧", "IHOT 爱喜剧", "IHOT爱喜剧", "ihot爱喜剧", "爱喜剧", "ihot 爱喜剧"],
    "iHOT爱科幻": ["iHOT 爱科幻", "IHOT 爱科幻", "IHOT爱科幻", "ihot爱科幻", "爱科幻", "ihot 爱科幻"],
    "iHOT爱院线": ["iHOT 爱院线", "IHOT 爱院线", "IHOT爱院线", "ihot爱院线", "ihot 爱院线", "爱院线"],
    "iHOT爱悬疑": ["iHOT 爱悬疑", "IHOT 爱悬疑", "IHOT爱悬疑", "ihot爱悬疑", "ihot 爱悬疑", "爱悬疑"],
    "iHOT爱历史": ["iHOT 爱历史", "IHOT 爱历史", "IHOT爱历史", "ihot爱历史", "ihot 爱历史", "爱历史"],
    "iHOT爱谍战": ["iHOT 爱谍战", "IHOT 爱谍战", "IHOT爱谍战", "ihot爱谍战", "ihot 爱谍战", "爱谍战"],
    "iHOT爱旅行": ["iHOT 爱旅行", "IHOT 爱旅行", "IHOT爱旅行", "ihot爱旅行", "ihot 爱旅行", "爱旅行"],
    "iHOT爱幼教": ["iHOT 爱幼教", "IHOT 爱幼教", "IHOT爱幼教", "ihot爱幼教", "ihot 爱幼教", "爱幼教"],
    "iHOT爱玩具": ["iHOT 爱玩具", "IHOT 爱玩具", "IHOT爱玩具", "ihot爱玩具", "ihot 爱玩具", "爱玩具"],
    "iHOT爱体育": ["iHOT 爱体育", "IHOT 爱体育", "IHOT爱体育", "ihot爱体育", "ihot 爱体育", "爱体育"],
    "iHOT爱赛车": ["iHOT 爱赛车", "IHOT 爱赛车", "IHOT爱赛车", "ihot爱赛车", "ihot 爱赛车", "爱赛车"],
    "iHOT爱浪漫": ["iHOT 爱浪漫", "IHOT 爱浪漫", "IHOT爱浪漫", "ihot爱浪漫", "ihot 爱浪漫", "爱浪漫"],
    "iHOT爱奇谈": ["iHOT 爱奇谈", "IHOT 爱奇谈", "IHOT爱奇谈", "ihot爱奇谈", "ihot 爱奇谈", "爱奇谈"],
    "iHOT爱科学": ["iHOT 爱科学", "IHOT 爱科学", "IHOT爱科学", "ihot爱科学", "ihot 爱科学", "爱科学"],
    "iHOT爱动漫": ["iHOT 爱动漫", "IHOT 爱动漫", "IHOT爱动漫", "ihot爱动漫", "ihot 爱动漫", "爱动漫"],
    "东北热剧": ["NewTV东北热剧", "NewTV 东北热剧", "newtv 东北热剧", "NEWTV 东北热剧", "NEWTV东北热剧"],
    "中国功夫": ["NewTV中国功夫", "NewTV 中国功夫", "newtv 中国功夫", "NEWTV 中国功夫", "NEWTV中国功夫"],
    "动作电影": ["NewTV动作电影", "NewTV 动作电影", "newtv 动作电影", "NEWTV 动作电影", "NEWTV动作电影"],
    "军事评论": ["NewTV军事评论", "NewTV 军事评论", "newtv 军事评论", "NEWTV 军事评论", "NEWTV军事评论"],
    "军旅剧场": ["NewTV军旅剧场", "NewTV 军旅剧场", "newtv 军旅剧场", "NEWTV 军旅剧场", "NEWTV军旅剧场"],
    "魅力潇湘": ["NewTV魅力潇湘", "NewTV 魅力潇湘", "newtv 魅力潇湘", "NEWTV 魅力潇湘", "NEWTV魅力潇湘"],
    "古装剧场": ["NewTV古装剧场", "NewTV 古装剧场", "newtv 古装剧场", "NEWTV 古装剧场", "NEWTV古装剧场"],
    "家庭剧场": ["NewTV家庭剧场", "NewTV 家庭剧场", "newtv 家庭剧场", "NEWTV 家庭剧场", "NEWTV家庭剧场"],
    "惊悚悬疑": ["NewTV惊悚悬疑", "NewTV 惊悚悬疑", "newtv 惊悚悬疑", "NEWTV 惊悚悬疑", "NEWTV惊悚悬疑"],
    "明星大片": ["NewTV明星大片", "NewTV 明星大片", "newtv 明星大片", "NEWTV 明星大片", "NEWTV明星大片"],
    "欢乐剧场": ["NewTV欢乐剧场", "NewTV 欢乐剧场", "newtv 欢乐剧场", "NEWTV 欢乐剧场", "NEWTV欢乐剧场"],
    "海外剧场": ["NewTV海外剧场", "NewTV 海外剧场", "newtv 海外剧场", "NEWTV 海外剧场", "NEWTV海外剧场"],
    "潮妈辣婆": ["NewTV潮妈辣婆", "NewTV 潮妈辣婆", "newtv 潮妈辣婆", "NEWTV 潮妈辣婆", "NEWTV潮妈辣婆"],
    "爱情喜剧": ["NewTV爱情喜剧", "NewTV 爱情喜剧", "newtv 爱情喜剧", "NEWTV 爱情喜剧", "NEWTV爱情喜剧"],
    "炫舞未来": ["NewTV炫舞未来", "NewTV 炫舞未来", "newtv 炫舞未来", "NEWTV 炫舞未来", "NEWTV炫舞未来"],
    "精品体育": ["NewTV精品体育", "NewTV 精品体育", "newtv 精品体育", "NEWTV 精品体育", "NEWTV精品体育"],
    "精品大剧": ["NewTV精品大剧", "NewTV 精品大剧", "newtv 精品大剧", "NEWTV 精品大剧", "NEWTV精品大剧"],
    "精品纪录": ["NewTV精品纪录", "NewTV 精品纪录", "newtv 精品纪录", "NEWTV 精品纪录", "NEWTV精品纪录"],
    "精品萌宠": ["NewTV精品萌宠", "NewTV 精品萌宠", "newtv 精品萌宠", "NEWTV 精品萌宠", "NEWTV精品萌宠"],
    "超级体育": ["NewTV超级体育", "NewTV 超级体育", "newtv 超级体育", "NEWTV 超级体育", "NEWTV超级体育"],
    "超级电影": ["NewTV超级电影", "NewTV 超级电影", "newtv 超级电影", "NEWTV 超级电影", "NEWTV超级电影"],
    "怡伴健康": ["NewTV怡伴健康", "NewTV 怡伴健康", "newtv 怡伴健康", "NEWTV 怡伴健康", "NEWTV怡伴健康"],
    "超级电视剧": ["NewTV超级电视剧", "NewTV 超级电视剧", "newtv 超级电视剧", "NEWTV 超级电视剧", "NEWTV超级电视剧"],
    "超级综艺": ["NewTV超级综艺", "NewTV 超级综艺", "newtv 超级综艺", "NEWTV 超级综艺", "NEWTV超级综艺"],
    "金牌综艺": ["NewTV金牌综艺", "NewTV 金牌综艺", "newtv 金牌综艺", "NEWTV 金牌综艺", "NEWTV金牌综艺"],
    "武搏世界": ["NewTV武搏世界", "NewTV 武搏世界", "newtv 武搏世界", "NEWTV 武搏世界", "NEWTV武搏世界"],
    "农业致富": ["NewTV农业致富", "NewTV 农业致富", "newtv 农业致富", "NEWTV 农业致富", "NEWTV农业致富"],
}

# -------------------------
# 正则
# -------------------------
ipv6_regex = r"http://\[[0-9a-fA-F:]+\]"  # 匹配 IPv6 地址

def normalize_channel_name(name: str) -> str:
    """根据别名映射表统一频道名称"""
    for standard, aliases in CHANNEL_MAPPING.items():
        if name == standard or name in aliases:
            return standard
    return name
# -------------------------
# -------------------------
# 正则表达式添加区域
# -------------------------
# -------------------------
def is_invalid_url(url: str) -> bool:
    """检查是否为无效 URL（可扩展过滤规则）"""
    hlj = r"http://\[[a-fA-F0-9:]+\](?::\d+)?/ottrrs\.hl\.chinamobile\.com/.+/.+" # 黑龙江移动V6
    hlj1 = r"http://\[2409:8087:1a01:df::7005\]/.*"# 黑龙江移动V6


    if re.match(hlj, url) or re.match(hlj1, url):
        return True

    return False

# -------------------------
# 抓取 URL
# -------------------------
def fetch_lines(url: str):
    """下载并分行返回内容"""
    try:
        resp = requests.get(url, timeout=15)
        resp.encoding = "utf-8"
        return resp.text.splitlines()
    except Exception as e:
        print(f"❌ 获取失败 {url}: {e}")
        return []

# -------------------------
# 解析 M3U / TXT
# -------------------------
def parse_lines(lines):
    """解析 M3U 或 TXT 内容，返回 {频道名: [url列表]}"""
    channels_dict = defaultdict(list)
    current_name = None

    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue

        # M3U #EXTINF 格式
        if line.startswith("#EXTINF"):
            if "," in line:
                current_name = line.split(",")[-1].strip()
            if i + 1 < len(lines):
                url = lines[i + 1].strip()
                url = url.split("$")[0].strip()  # 去掉 $ 后缀
                if re.match(ipv6_regex, url) and not is_invalid_url(url):
                    norm_name = normalize_channel_name(current_name)
                    channels_dict[norm_name].append(url)
            current_name = None

        # TXT 频道名,URL 格式
        elif "," in line:
            parts = line.split(",", 1)
            if len(parts) == 2:
                ch_name, url = parts[0].strip(), parts[1].strip()
                url = url.split("$")[0].strip()  # 去掉 $ 后缀
                if re.match(ipv6_regex, url) and not is_invalid_url(url):
                    norm_name = normalize_channel_name(ch_name)
                    channels_dict[norm_name].append(url)

    return channels_dict

# -------------------------
# 生成 M3U 文件
# -------------------------
def create_m3u_file(all_channels, filename="ipv6.m3u"):
    """生成带分类的 M3U 文件，一频道多源连续写"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write('#EXTM3U x-tvg-url="https://kakaxi-1.github.io/IPTV/epg.xml"\n\n')
        for group, channel_list in CHANNEL_CATEGORIES.items():
            for ch in channel_list:
                if ch in all_channels and all_channels[ch]:
                    # 去重 URL，保留顺序
                    unique_urls = list(dict.fromkeys(all_channels[ch]))
                    logo = f"https://kakaxi-1.github.io/IPTV/LOGO/{ch}.png"
                    f.write(f'#EXTINF:-1 tvg-name="{ch}" tvg-logo="{logo}" group-title="{group}",{ch}\n')
                    for url in unique_urls:
                        f.write(f"{url}\n")

# -------------------------
# 主函数
# -------------------------
def main():
    urls = [
        "https://raw.githubusercontent.com/kakaxi-1/IPTV/main/ipv6.m3u",
        #"https？://**/***/m3u/txt",
        # 可添加更多源
    ]

    all_channels = defaultdict(list)

    for url in urls:
        lines = fetch_lines(url)
        parsed = parse_lines(lines)
        for ch, urls_list in parsed.items():
            all_channels[ch].extend(urls_list)  # 一频道多源都保留

    create_m3u_file(all_channels)
    print(f"✅ 已生成 ipv6.m3u，频道数: {len(all_channels)}")

if __name__ == "__main__":
    main()