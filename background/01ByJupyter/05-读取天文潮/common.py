# TODO:[-] 23-01-19
# 由于 东山 与 岱山的 code 均为 DSH 暂时不录入这两个站点
# TODO:[-] 23-12-28 更新了站点字典,以此为准
DICT_STATION = {
    'DONGGANG': 'DGG',
    'XIAOCS': 'XCS',
    'LAOHUTAN': 'LHT',
    'BAYUQUAN': 'BYQ',
    'YINGKOU': 'YKO',
    'HULUDAO': 'HLD',
    'ZHIMAOW': 'ZMW',
    'QINHUANG': 'QHD',
    'TANGGU': 'TGU',
    'CAOFD': 'CFD',
    'HUANGHUA': 'HHA',
    'BINZHOU': 'BZG',
    'DONGYING': 'DYG',
    'YANGJIAO': 'YJG',
    'WEIFANG': 'WFG',
    'LONGKOU': 'LKO',
    'PENGLAI': 'PLI',
    # 'YANTAI': 'YTI',  # TODO:[-] 实际不存在
    'XIAOSHID': 'XSD',
    'CHENGST': 'CST',
    'WENDENG': 'WDG',
    'SHIDAO': 'SID',
    'QIANLIY': 'QLY',
    'QINGDAOH': 'WMT',  # TODO:[*] 是否有问题
    'XIAOMAID': 'XMD',
    'SHIJIUS': 'RZH',
    'LANSHAN': 'LSH',
    'LIANYUNG': 'LYG',
    'YANWEI': 'YWI',
    'WKJIAO': 'YKG',
    'LUSI': 'LSI',
    'PUZHEN': 'BZH',
    'WUSONG': 'WSG',
    'GAOQIAO': 'GQA',
    'COMIN': 'CMG',
    # ----
    #     # 区域2
    # 芦潮港  10 711
    'LUCHAOG': 'LCG',
    # 大戢山  11 730
    # 'DAISHAN': 'DJS', # 没有大吉山
    # # 金山嘴  17 684
    'JINSHAN': 'JSZ',
    # # 滩浒    23 697
    # 3: 'TXU',       # TODO:[*] 22-06-21 没有滩浒的天文潮文件(2021)
    # 乍浦    26 667
    'ZHAPU': 'ZPU',
    # 澉浦    39 655
    # 5: 'GPU',   # TODO:[*] 22-06-21 没有澉浦的天文潮文件(2021) 注意 db 更新澉浦 GPU
    # 嵊山    17 768
    'SHENGSHAN': 'SHS',
    # 岱山    46 731
    # 'DAISHAN': 'DSH',
    # 定海    61 724
    'DINGHAI': 'DHI',
    # 镇海    61 704
    'ZHENHAIH': 'ZHI',
    # 沈家门  64 737
    'SHENJIAMEN': 'SJM',
    # 北仑    65 727
    'BEILUN': 'BLN',
    # 乌沙山  90 699
    'WUSS': 'WSH',
    # 石浦   106 719
    'SHIPU': 'SPU',
    # 健跳   117 699
    'JIANTIAO': 'JAT',
    # 海门Z  139 687
    'HAIMENZ': 'HMZ',  # TODO:[*] 22-06-21 天文潮位有两个，需对应
    # 大陈   153 714
    'DACHEN': 'DCH',
    # 坎门   175 679
    'KANMEN': 'KMN',
    # 温州S  181 645
    'WENZHOU2': 'WZS',
    # 瑞安S  197 641
    'RUIAN': 'RAS',
    # 鳌江S  206 638
    'AOJIANG': 'AJS',  # 没有鳌江S
    # 沙埕S  230 625
    'SHACHENG': 'SCS',  # 还有SHACHENGH
    # 秦屿   238 617
    'QINYU': 'QYU',
    # 三沙   246 614
    'SANSHA': 'SHA',
    # 北礵   258 621
    'BEISHUANG': 'BSH',
    # 城澳   263 584
    'CHENGAO': 'CAO',
    # 青屿   279 582
    'QINGYU': 'QGY',
    # 北茭   278 596
    'BJIAO': 'BJA',
    # 琯头   293 575
    'GUANTOU': 'GTO',
    # 梅花   299 581
    'MEIHUA': 'MHA',
    # 白岩潭 297 572
    'BAIYANT': 'BYT',
    # 平潭   332 590
    'PINGTANf': 'PTN',
    # 福清核 334 566
    'FUQINGHD': 'FQH',
    # 石城   344 562
    'SHICHENG': 'SHC',
    # 峰尾   353 538
    'FENGWEI': 'FHW',
    # 崇武H  368 536
    'CHONGWUH': 'CHW',
    # 晋江   382 520
    'JINJIANG': 'JJH',
    # 石井   381 507
    'SHIJING': 'SJH',
    # 厦门   393 484
    'XIAMEN': 'XMN',
    # 旧镇   421 463
    'JIUZHENG': 'JZH',
    # 古雷   432 459
    'GULEI': 'GUL',
    # 东山   436 452
    # 'DONGSHAN': 'DSH',
    # 赤石湾 442 434
    'CHISHIWAN': 'CSW',
    # 云澳   457 427
    'YUNAO': 'YAO',
    # 汕头S  460 405
    'SHANTOU': 'STO',
    # 海门G  470 397
    # TODO:[-] 22-08-14 注意应改为 HAIMENG22022
    'HAIMENG2': 'HMN',
    # 'HAIMENZ': 'HMN',  # 存在两个海门
    # 'HAIMENZ': 'HMZ',  # 海门Z
    # 惠来   482 392
    'HUILAI': 'HLA',
    # 陆丰   491 366
    'LUFENG': 'LFG',
    # 遮浪   501 334
    'ZHELANG': 'ZHL',
    # 汕尾   495 321
    'SHANWEI': 'SHW',
    # 惠州   497 275
    'HUIZHOU': 'HZO',
    # 盐田   506 257
    'YANTIAN': 'YTA',
    # 赤湾H  513 233
    # 'CHIWANH': 'CHH',
    # 南沙   496 215
    # 'NANSHA': 'GNS',  # 注意存在两个南沙
    # 黄埔   491 216
    'HUANGPU': 'HPU',  # 存在两个黄埔，黄埔与黄埔G
    # 珠海   523 216
    'ZHUHAI': 'ZHU',
    # 灯笼山 534 208
    'DENGLONG': 'DLS',
    # 三灶   539 205
    'SANZAO': 'SZA',

    'ZHAPO': 'ZHP',
    'SHUIDONG': 'SHD',
    'ZHANJS': 'ZJS',
    #     # 31: 'ZJS', # TODO:[-] 22-06-30 注意有两个ZJS
    'NAOZHOU': 'NAZ',
    'NANDU': 'NAD',
    'HAIAN': 'HAN',
    'XIUYING': 'XYG',
    'QINGLANH': 'QLN',
    'BOAO': 'BAO',
    'SANYA': 'SYA',
    'DONGFANG': 'DFG',
    'SHITOUPU': 'STP',
    'WEIZHOU': 'WZH',
    'BEIHAI': 'BHI',
    'QINZHOU': 'QZH',
    'FANGCG': 'FCG',
    'WUCHANG': 'WCH',
    'YINGGEH': 'YGH',
    # TODO:[-] 23-12-28 统一修改天文潮 name:code 对应关系
    'RAOPING': 'RPG', 'HENGMEN': 'HGM', 'MAGE': 'MGE', 'TAISHAN': 'TSH', 'BEIJIN': 'BJN',
    # 'ZHUHAI': 'ZHU',
    'TANTOU': 'TNT',
    'LEIZHOU': 'LZH',
    'CHIWANH': 'CWH',
    'NANSHA': 'NSA',
    'HUANGPUG': 'HPG',  # 上海黄埔公园
    'DONGTOU': 'DTO',  # 洞头
    'LONGWAN': 'LGW',  # 龙湾
    'CHMEN': 'CGM',  # 长门
    'GANPU': 'GPU',  # 澉浦
    'PINGTAN': 'PTN',  # 平潭
    'SZDONGSHAN': 'DSH',  # 深圳东山
    'GANGBEI': 'GBE',  # 港北
    'GUDONG': 'GUD',  # 孤东
    'YANTAI': 'ZFD',  # 芝罘岛
    'DAISHAN': 'DAI',  # 芝罘岛
}
