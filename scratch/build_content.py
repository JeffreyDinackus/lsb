"""Builds app/src/data/content.json -- every section of the Lutheran Daily Office as a list of blocks.

Usage: python3 build_content.py

The orders follow the Lutheran Service Book (LSB). Canticles and fixed psalms are pulled from
the RSV-UE in ../bibles/rsvue-bible.json so the scripture text matches the lectionary readings.
Block types mirror app/src/types.ts. Inline **bold** marks words said by all (the LSB convention).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIBLE = json.loads((ROOT / 'bibles/rsvue-bible.json').read_text(encoding='utf-8-sig'))
SUPERSCRIPT_RE = re.compile(r'^[\s⁰¹²³⁴⁵⁶⁷⁸⁹]+')


def find_book(name):
    for testament in BIBLE.values():
        if name in testament:
            return testament[name]
    raise KeyError(name)


# ---------- block helpers ----------

def H(text):
    return {'type': 'heading', 'text': text}


def SUB(text):
    return {'type': 'subtitle', 'text': text}


def SH(text):
    return {'type': 'small-heading', 'text': text}


def R(text):
    return {'type': 'rubric', 'text': text}


def P(text, citation=None):
    b = {'type': 'paragraph', 'text': text}
    if citation:
        b['citation'] = citation
    return b


def L(text, citation=None):
    b = {'type': 'dialogue', 'label': 'L', 'text': text}
    if citation:
        b['citation'] = citation
    return b


def C(text, citation=None):
    b = {'type': 'dialogue', 'label': 'C', 'text': text, 'strong': True}
    if citation:
        b['citation'] = citation
    return b


def V(lines, plain=False, citation=None):
    """A said/prayed text broken into lines. Bold (all say it) unless plain."""
    verse = {'number': None, 'lines': lines}
    if citation:
        verse['citation'] = citation
    b = {'type': 'verse-block', 'verses': [verse]}
    if plain:
        b['plain'] = True
    return b


def LECT(office, role):
    return {'type': 'lectionary-reading', 'office': office, 'role': role}


def COLS(rows):
    return {'type': 'columns', 'rows': rows}


def WEEKDAY():
    return {'type': 'weekday-intention'}


def scripture(book, chapter, verse_spec, plain=True, gloria=False, citation=None):
    """verse_spec like '1-7' or '1-4,8'. Returns a verse-block with RSV-UE verse numbers."""
    ch = find_book(book)[str(chapter)]
    numbers = []
    for part in verse_spec.split(','):
        if '-' in part:
            a, b = part.split('-')
            numbers.extend(range(int(a), int(b) + 1))
        else:
            numbers.append(int(part))
    verses = []
    for n in numbers:
        raw = SUPERSCRIPT_RE.sub('', ch[str(n)])
        lines = [ln.strip() for ln in raw.split('\n') if ln.strip()]
        verses.append({'number': str(n), 'lines': lines})
    if gloria:
        verses.append({'number': None, 'lines': GLORIA_LINES})
    if citation:
        verses[-1]['citation'] = citation
    b = {'type': 'verse-block', 'verses': verses}
    if plain:
        b['plain'] = True
    return b


# ---------- common texts ----------

GLORIA_LINES = [
    'Glory be to the Father and to the Son and to the Holy Spirit;',
    'as it was in the beginning, is now, and will be forever. Amen.',
]
GLORIA = V(GLORIA_LINES)

INVOCATION = [
    R('The sign of the cross ✠ may be made by all in remembrance of their Baptism.'),
    V(['In the name of the Father and of the ✠ Son and of the Holy Spirit.', '**Amen.**'], plain=True),
]

APOSTLES_CREED = V([
    'I believe in God, the Father Almighty,',
    'maker of heaven and earth.',
    'And in Jesus Christ, His only Son, our Lord,',
    'who was conceived by the Holy Spirit,',
    'born of the virgin Mary,',
    'suffered under Pontius Pilate,',
    'was crucified, died and was buried.',
    'He descended into hell.',
    'The third day He rose again from the dead.',
    'He ascended into heaven',
    'and sits at the right hand of God the Father Almighty.',
    'From thence He will come to judge the living and the dead.',
    'I believe in the Holy Spirit,',
    'the holy Christian Church,',
    'the communion of saints,',
    'the forgiveness of sins,',
    'the resurrection of the body,',
    'and the life ✠ everlasting. Amen.',
])

LORDS_PRAYER = V([
    'Our Father who art in heaven,',
    'hallowed be Thy name,',
    'Thy kingdom come,',
    'Thy will be done on earth as it is in heaven;',
    'give us this day our daily bread;',
    'and forgive us our trespasses',
    'as we forgive those who trespass against us;',
    'and lead us not into temptation,',
    'but deliver us from evil.',
    'For Thine is the kingdom and the power and the glory',
    'forever and ever. Amen.',
])

KYRIE = [
    L('Lord, have mercy.'),
    C('Christ, have mercy. Lord, have mercy.'),
]

ALLELUIA_RUBRIC = R('Alleluia is omitted during Lent.')

OPENING_VERSICLES = [
    L('O Lord, open my lips,'),
    C('and my mouth will declare Your praise.', 'Psalm 51:15'),
    L('Make haste, O God, to deliver me;'),
    C('make haste to help me, O Lord.', 'Psalm 70:1'),
    L('Glory be to the Father and to the Son and to the Holy Spirit;'),
    C('as it was in the beginning, is now, and will be forever. Amen. Alleluia.'),
    ALLELUIA_RUBRIC,
]

COLLECT_FOR_GRACE = P(
    'O Lord, our heavenly Father, almighty and everlasting God, You have safely brought us to the '
    'beginning of this day. Defend us in the same with Your mighty power and grant that this day we fall '
    'into no sin, neither run into any kind of danger, but that all our doings, being ordered by Your '
    'governance, may be righteous in Your sight; through Jesus Christ, Your Son, our Lord, who lives and '
    'reigns with You and the Holy Spirit, one God, now and forever. **Amen.**')

COLLECT_FOR_PEACE = P(
    'O God, from whom come all holy desires, all good counsels, and all just works, give to us, Your '
    'servants, that peace which the world cannot give, that our hearts may be set to obey Your '
    'commandments and also that we, being defended from the fear of our enemies, may live in peace and '
    'quietness; through Jesus Christ, Your Son, our Lord, who lives and reigns with You and the Holy '
    'Spirit, one God, now and forever. **Amen.**')

COLLECT_AGAINST_PERILS = P(
    'Lighten our darkness, we beseech You, O Lord, and by Your great mercy defend us from all perils and '
    'dangers of this night; for the love of Your only Son, our Savior, Jesus Christ. **Amen.**')

LUTHER_MORNING = P(
    '**I thank You, my heavenly Father, through Jesus Christ, Your dear Son, that You have kept me this '
    'night from all harm and danger; and I pray that You would keep me this day also from sin and every '
    'evil, that all my doings and life may please You. For into Your hands I commend myself, my body and '
    'soul, and all things. Let Your holy angel be with me, that the evil foe may have no power over me. '
    'Amen.**', 'Small Catechism')

LUTHER_EVENING = P(
    '**I thank You, my heavenly Father, through Jesus Christ, Your dear Son, that You have graciously kept '
    'me this day; and I pray that You would forgive me all my sins where I have done wrong, and graciously '
    'keep me this night. For into Your hands I commend myself, my body and soul, and all things. Let Your '
    'holy angel be with me, that the evil foe may have no power over me. Amen.**', 'Small Catechism')

BENEDICAMUS = [
    L('Let us bless the Lord.'),
    C('Thanks be to God.'),
]

BENEDICTION_GRACE = [
    L('The grace of our Lord Jesus Christ and the love of God and the communion of the Holy Spirit be '
      'with you all.', '2 Corinthians 13:14'),
    C('Amen.'),
]

BENEDICTION_TRINITY = [
    L('The almighty and merciful Lord, the Father, the ✠ Son, and the Holy Spirit, bless and preserve us.'),
    C('Amen.'),
]

TE_DEUM = V([
    'We praise You, O God;',
    'we acknowledge You to be the Lord.',
    'All the earth now worships You,',
    'the Father everlasting.',
    'To You all angels cry aloud,',
    'the heavens and all the powers therein;',
    'to You cherubim and seraphim continually do cry:',
    'Holy, holy, holy, Lord God of Sabaoth;',
    'heaven and earth are full of the majesty of Your glory.',
    'The glorious company of the apostles praise You.',
    'The goodly fellowship of the prophets praise You.',
    'The noble army of martyrs praise You.',
    'The holy Church throughout all the world does acknowledge You:',
    'the Father of an infinite majesty;',
    'Your adorable, true, and only Son;',
    'also the Holy Spirit, the Comforter.',
    'You are the King of glory, O Christ;',
    'You are the everlasting Son of the Father.',
    'When You took upon Yourself to deliver man,',
    'You humbled Yourself to be born of a virgin.',
    'When You had overcome the sharpness of death,',
    'You opened the kingdom of heaven to all believers.',
    'You sit at the right hand of God in the glory of the Father.',
    'We believe that You will come to be our judge.',
    'We therefore pray You to help Your servants,',
    'whom You have redeemed with Your precious blood.',
    'Make them to be numbered with Your saints',
    'in glory everlasting.',
    'O Lord, save Your people and bless Your heritage;',
    'govern them and lift them up forever.',
    'Day by day we magnify You,',
    'and we worship Your name forever, world without end.',
    'Grant, O Lord, to keep us this day without sin.',
    'O Lord, have mercy upon us; have mercy upon us.',
    'O Lord, let Your mercy be upon us, as our trust is in You.',
    'O Lord, in You have I trusted; let me never be confounded.',
])

PHOS_HILARON = V([
    'Joyous light of glory',
    'of the immortal Father;',
    'heavenly, holy, blessed Jesus Christ.',
    'Now that we have come to the setting of the sun',
    'and behold the evening light,',
    'we praise God: Father, Son, and Holy Spirit.',
    'You are worthy at all times',
    'to be praised with happy voices,',
    'O Son of God, O Giver of life,',
    'and to be glorified through all the worlds.',
])

COMPLINE_HYMN = V([
    'Before the ending of the day,',
    'Creator of the world, we pray',
    'That with Thy wonted favor Thou',
    'Wouldst be our guard and keeper now.',
    '',
    'From all ill dreams defend our eyes,',
    'From nightly fears and fantasies;',
    'Tread under foot our ghostly foe,',
    'That no pollution we may know.',
    '',
    'O Father, that we ask be done,',
    'Through Jesus Christ, Thine only Son,',
    'Who, with the Holy Ghost and Thee,',
    'Doth live and reign eternally. Amen.',
], plain=True, citation='Te lucis ante terminum; tr. John Mason Neale')

WEEKDAY_TOPICS = [
    ['Sunday', 'For the joy of the resurrection among us; for the fruit of faith nourished by the Word and the Sacraments.'],
    ['Monday', 'For faith to live in the promises of Holy Baptism; for one’s calling and daily work; for the unemployed; for the salvation and well-being of our neighbors; for schools, colleges, and seminaries; for good government and for peace.'],
    ['Tuesday', 'For deliverance against temptation and evil; for the addicted and despairing, the tortured and oppressed; for those struggling with sin.'],
    ['Wednesday', 'For marriage and family, that husbands and wives, parents and children live in ordered harmony according to the Word of God; for parents who must raise children alone; for our communities and neighborhoods.'],
    ['Thursday', 'For the Church and her pastors; for teachers, deaconesses, and other church workers; for missionaries and for all who serve the Church; for fruitful and salutary use of the blessed Sacrament of Christ’s body and blood.'],
    ['Friday', 'For the preaching of the holy cross of our Lord Jesus Christ and for the spread of His knowledge throughout the whole world; for the persecuted and oppressed; for the sick and dying.'],
    ['Saturday', 'For faithfulness to the end; for the renewal of those who are withering in the faith or have fallen away; for receptive hearts and minds to God’s Word on the Lord’s Day; for pastors and people as they prepare to administer and receive Christ’s holy gifts.'],
]


# ---------- the offices ----------

matins = [
    H('Matins'),
    R('A hymn of invocation may be sung.'),
    R('Stand'),
    *OPENING_VERSICLES,

    H('Psalmody'),
    SH('VENITE • O Come, Let Us Sing'),
    R('The common or seasonal antiphon is sung or said before and after the Venite.'),
    L('Oh, come, let us worship Him.'),
    C('Blessed be God, the Father, the Son, and the Holy Spirit.'),
    scripture('Psalm', 95, '1-7', gloria=True, citation='Psalm 95:1–7'),
    L('Oh, come, let us worship Him.'),
    C('Blessed be God, the Father, the Son, and the Holy Spirit.'),
    R('Sit'),
    SH('PSALM'),
    R('The psalm(s) appointed for the day are sung or said. Each psalm concludes with the Gloria Patri.'),
    LECT('morning', 'psalm'),
    GLORIA,
    SH('OFFICE HYMN'),
    R('The Office Hymn is sung.'),

    H('Readings'),
    R('The appointed reading is read.'),
    LECT('morning', 'lesson'),
    R('After the reading:'),
    L('O Lord, have mercy on us.'),
    C('Thanks be to God.'),
    SH('RESPONSORY'),
    L('Your word is a lamp to my feet'),
    C('and a light to my path.', 'Psalm 119:105'),
    L('Blessed are those who hear the word of God and keep it.'),
    C('Your word is a lamp to my feet and a light to my path.', 'Luke 11:28'),
    L('Glory be to the Father and to the Son and to the Holy Spirit.'),
    C('Your word is a lamp to my feet and a light to my path.'),
    R('A sermon may follow.'),
    R('Stand'),
    SH('CANTICLE • TE DEUM LAUDAMUS'),
    R('The Te Deum or the Benedictus (see Morning Prayer) is sung.'),
    TE_DEUM,

    H('Prayer'),
    R('Kneel/Stand'),
    *KYRIE,
    LORDS_PRAYER,
    R('The Collect of the Day is prayed.'),
    L('The Lord be with you.'),
    C('And with your spirit.'),
    L('Let us pray.'),
    R('Collect of the Day'),
    SH('COLLECT FOR GRACE'),
    COLLECT_FOR_GRACE,
    SH('BENEDICAMUS'),
    *BENEDICAMUS,
    SH('BENEDICTION'),
    *BENEDICTION_GRACE,
]

vespers = [
    H('Vespers'),
    R('A hymn of invocation may be sung.'),
    R('Stand'),
    L('O Lord, come to my aid;'),
    C('make haste to help me, O Lord.', 'Psalm 70:1'),
    L('Glory be to the Father and to the Son and to the Holy Spirit;'),
    C('as it was in the beginning, is now, and will be forever. Amen. Alleluia.'),
    ALLELUIA_RUBRIC,

    H('Psalmody'),
    R('Sit'),
    R('The psalm(s) appointed for the evening are sung or said. Each psalm concludes with the Gloria Patri.'),
    LECT('evening', 'psalm'),
    GLORIA,
    SH('OFFICE HYMN'),
    R('The Office Hymn is sung.'),

    H('Readings'),
    R('The appointed reading is read.'),
    LECT('evening', 'lesson'),
    R('After the reading:'),
    L('O Lord, have mercy on us.'),
    C('Thanks be to God.'),
    SH('RESPONSORY'),
    L('In many and various ways God spoke to His people of old by the prophets.'),
    C('But now in these last days He has spoken to us by His Son.', 'Hebrews 1:1–2'),
    L('Glory be to the Father and to the Son and to the Holy Spirit.'),
    C('But now in these last days He has spoken to us by His Son.'),
    R('A sermon may follow.'),
    R('Stand'),
    SH('CANTICLE • MAGNIFICAT'),
    R('The Magnificat or the Nunc Dimittis is sung.'),
    scripture('Luke', 1, '46-55', plain=False, gloria=True, citation='Luke 1:46–55'),

    H('Prayer'),
    R('Kneel/Stand'),
    *KYRIE,
    LORDS_PRAYER,
    L('The Lord be with you.'),
    C('And with your spirit.'),
    L('Let us pray.'),
    R('Collect of the Day'),
    SH('COLLECT FOR PEACE'),
    COLLECT_FOR_PEACE,
    SH('BENEDICAMUS'),
    *BENEDICAMUS,
    SH('BENEDICTION'),
    *BENEDICTION_GRACE,
]

morning_prayer = [
    H('Morning Prayer'),
    R('Stand'),
    *OPENING_VERSICLES,
    SH('PASCHAL BLESSING'),
    R('On Sundays, especially during the Easter season, the Paschal Blessing may be said.'),
    L('Alleluia! Christ is risen.'),
    C('He is risen indeed. Alleluia!'),
    scripture('Luke', 24, '1-7', citation='Luke 24:1–7'),
    L('Let us bless the Lord.'),
    C('Thanks be to God. Alleluia!'),

    H('Psalmody'),
    SH('VENITE'),
    scripture('Psalm', 95, '1-7', gloria=True, citation='Psalm 95:1–7'),
    R('Sit'),
    SH('PSALM'),
    R('The psalm(s) appointed for the day are sung or said. Each concludes with the Gloria Patri.'),
    LECT('morning', 'psalm'),
    GLORIA,
    R('Silence for meditation'),
    SH('OFFICE HYMN'),
    R('The Office Hymn is sung.'),

    H('Readings'),
    LECT('morning', 'lesson'),
    R('After the reading:'),
    L('O Lord, have mercy on us.'),
    C('Thanks be to God.'),
    SH('RESPONSORY'),
    L('Lord, You have the words of eternal life.'),
    C('We have believed, and have come to know, that You are the Holy One of God.', 'John 6:68–69'),
    R('A sermon may follow.'),
    R('Stand'),
    SH('CANTICLE • BENEDICTUS'),
    scripture('Luke', 1, '68-79', plain=False, gloria=True, citation='Luke 1:68–79'),

    H('Prayers'),
    R('Kneel/Stand'),
    SH('LITANY'),
    L('Lord, have mercy upon us.'),
    C('Christ, have mercy upon us. Lord, have mercy upon us.'),
    L('Show us Your steadfast love, O Lord,'),
    C('and grant us Your salvation.', 'Psalm 85:7'),
    L('Create in me a clean heart, O God,'),
    C('and renew a right spirit within me.', 'Psalm 51:10'),
    L('Cast me not away from Your presence,'),
    C('and take not Your Holy Spirit from me.', 'Psalm 51:11'),
    LORDS_PRAYER,
    R('Collect of the Day'),
    R('Other prayers may be offered.'),
    SH('COLLECT FOR GRACE'),
    COLLECT_FOR_GRACE,
    SH('BENEDICAMUS'),
    *BENEDICAMUS,
    SH('BLESSING'),
    *BENEDICTION_TRINITY,
]

evening_prayer = [
    H('Evening Prayer'),
    SH('SERVICE OF LIGHT'),
    R('Stand'),
    R('The candle may be carried in procession.'),
    L('Jesus Christ is the Light of the world,'),
    C('the light no darkness can overcome.', 'John 8:12; 1:5'),
    L('Stay with us, Lord, for it is evening,'),
    C('and the day is almost over.', 'Luke 24:29'),
    L('Let Your light scatter the darkness'),
    C('and illumine Your Church.'),
    SH('PHOS HILARON • Joyous Light of Glory'),
    PHOS_HILARON,
    SH('THANKSGIVING FOR LIGHT'),
    L('The Lord be with you.'),
    C('And with your spirit.'),
    L('Let us give thanks to the Lord our God.'),
    C('It is right to give Him thanks and praise.'),
    P('Blessed are You, O Lord our God, King of the universe, who led Your people Israel by a pillar of '
      'cloud by day and a pillar of fire by night. Enlighten our darkness by the light of Your Christ; let '
      'His Word be a lamp to our feet and a light to our path; for You are merciful, and You love Your whole '
      'creation, and we, Your creatures, glorify You, Father, Son, and Holy Spirit. **Amen.**'),

    H('Psalmody'),
    SH('PSALM 141'),
    R('The antiphon is sung or said before and after the psalm.'),
    C('Let my prayer rise before You as incense, the lifting up of my hands as the evening sacrifice.'),
    scripture('Psalm', 141, '1-4,8', gloria=True, citation='Psalm 141:1–4, 8'),
    C('Let my prayer rise before You as incense, the lifting up of my hands as the evening sacrifice.'),
    R('Silence for meditation'),
    P('Let the incense of our repentant prayer ascend before You, O Lord, and let Your loving-kindness '
      'descend upon us, that with purified minds we may sing Your praises with the Church on earth and the '
      'whole heavenly host and may glorify You forever and ever. **Amen.**'),
    R('Sit'),
    SH('PSALM'),
    R('The psalm(s) appointed for the evening are sung or said.'),
    LECT('evening', 'psalm'),
    GLORIA,
    SH('OFFICE HYMN'),
    R('The Office Hymn is sung.'),

    H('Readings'),
    LECT('evening', 'lesson'),
    R('After the reading:'),
    L('O Lord, have mercy on us.'),
    C('Thanks be to God.'),
    R('A sermon may follow.'),
    R('Stand'),
    SH('CANTICLE • MAGNIFICAT'),
    scripture('Luke', 1, '46-55', plain=False, gloria=True, citation='Luke 1:46–55'),

    H('Prayers'),
    SH('LITANY'),
    L('In peace let us pray to the Lord.'),
    C('Lord, have mercy.'),
    L('For the peace from above and for our salvation let us pray to the Lord.'),
    C('Lord, have mercy.'),
    L('For the peace of the whole world, for the well-being of the Church of God, and for the unity of all '
      'let us pray to the Lord.'),
    C('Lord, have mercy.'),
    L('For our homes and families, for our neighbors and friends, and for all who are dear to us let us '
      'pray to the Lord.'),
    C('Lord, have mercy.'),
    L('For those who travel, for the sick and the suffering, for the dying, and for all in any need let us '
      'pray to the Lord.'),
    C('Lord, have mercy.'),
    L('For a peaceful evening and a night of rest, and for a holy and quiet death, let us pray to the Lord.'),
    C('Lord, have mercy.'),
    L('Help, save, comfort, and defend us, gracious Lord.'),
    C('Amen.'),
    R('Silence for individual prayer'),
    LORDS_PRAYER,
    R('Collect of the Day'),
    SH('COLLECT FOR PEACE'),
    COLLECT_FOR_PEACE,
    SH('BENEDICAMUS'),
    *BENEDICAMUS,
    SH('BLESSING'),
    *BENEDICTION_TRINITY,
]

compline = [
    H('Compline'),
    SUB('Prayer at the Close of the Day'),
    R('Silence is kept.'),
    L('The Lord Almighty grant us a quiet night and peace at the last.'),
    C('Amen.'),
    L('It is good to give thanks to the Lord,'),
    C('to sing praise to Your name, O Most High;', 'Psalm 92:1'),
    L('to herald Your love in the morning,'),
    C('Your truth at the close of the day.', 'Psalm 92:2'),

    H('Confession'),
    L('Let us confess our sin in the presence of God.'),
    R('Silence for reflection and self-examination.'),
    V([
        'I confess to God Almighty, before the whole company of heaven and to you, my brothers and sisters,',
        'that I have sinned in thought, word, and deed by my fault, by my own fault, by my own most '
        'grievous fault; wherefore I pray God Almighty to have mercy on me, forgive me all my sins, and '
        'bring me to everlasting life. Amen.',
    ]),
    L('The almighty and merciful Lord grant you pardon, ✠ forgiveness, and remission of all your sins.'),
    C('Amen.'),
    R('The people may then confess to the leader:'),
    C('I confess to God Almighty, before the whole company of heaven and to you, my brother, that I have '
      'sinned in thought, word, and deed by my fault, by my own fault, by my own most grievous fault; '
      'wherefore I pray God Almighty to have mercy on me, forgive me all my sins, and bring me to '
      'everlasting life. Amen.'),
    L('The almighty and merciful Lord grant you pardon, ✠ forgiveness, and remission of all your sins.'),
    C('Amen.'),

    H('Psalmody'),
    R('One or more of the following psalms are sung or said: Psalm 4, 91, 134 (or 33, 34, 136, 139).'),
    SH('PSALM 4'),
    scripture('Psalm', 4, '1-8', gloria=True, citation='Psalm 4'),
    SH('PSALM 91'),
    scripture('Psalm', 91, '1-16', gloria=True, citation='Psalm 91'),
    SH('PSALM 134'),
    scripture('Psalm', 134, '1-3', gloria=True, citation='Psalm 134'),
    SH('OFFICE HYMN'),
    COMPLINE_HYMN,

    H('Readings'),
    R('One or more of the following readings is read.'),
    scripture('Jeremiah', 14, '9', citation='Jeremiah 14:9'),
    scripture('Matthew', 11, '28-30', citation='Matthew 11:28–30'),
    scripture('John', 14, '27', citation='John 14:27'),
    scripture('Romans', 8, '38-39', citation='Romans 8:38–39'),
    scripture('1 Peter', 5, '6-9', citation='1 Peter 5:6–9'),
    R('After the reading:'),
    L('O Lord, have mercy on us.'),
    C('Thanks be to God.'),
    SH('RESPONSORY'),
    L('Into Your hands, O Lord, I commend my spirit.'),
    C('Into Your hands, O Lord, I commend my spirit.'),
    L('You have redeemed us, O Lord, God of truth.'),
    C('I commend my spirit.', 'Psalm 31:5'),
    L('Glory be to the Father and to the Son and to the Holy Spirit.'),
    C('Into Your hands, O Lord, I commend my spirit.'),

    H('Prayers'),
    *KYRIE,
    LORDS_PRAYER,
    L('Into Your hands, O Lord, I commend my spirit;'),
    C('for You have redeemed me, O Lord, God of truth.'),
    L('Keep me as the apple of Your eye;'),
    C('hide me in the shadow of Your wings.', 'Psalm 17:8'),
    L('O Lord, hear my prayer,'),
    C('and let my cry come to You.', 'Psalm 102:1'),
    L('Let us pray.'),
    R('One or more of the following prayers is said.'),
    P('Visit our dwellings, O Lord, and drive from them all the snares of the enemy; let Your holy angels '
      'dwell with us to preserve us in peace; and let Your blessing be upon us always; through Jesus Christ, '
      'Your Son, our Lord, who lives and reigns with You and the Holy Spirit, one God, now and forever. '
      '**Amen.**'),
    COLLECT_AGAINST_PERILS,
    P('Be present, merciful God, and protect us through the hours of this night, so that we who are wearied '
      'by the changes and chances of this life may rest in Your eternal changelessness; through Jesus '
      'Christ, our Lord. **Amen.**'),
    LUTHER_EVENING,

    H('Nunc Dimittis'),
    R('The antiphon is sung or said before and after the canticle.'),
    C('Guide us waking, O Lord, and guard us sleeping, that awake we may watch with Christ and asleep we '
      'may rest in peace.'),
    scripture('Luke', 2, '29-32', plain=False, gloria=True, citation='Luke 2:29–32'),
    C('Guide us waking, O Lord, and guard us sleeping, that awake we may watch with Christ and asleep we '
      'may rest in peace.'),
    SH('BENEDICAMUS'),
    *BENEDICAMUS,
    SH('BENEDICTION'),
    *BENEDICTION_TRINITY,
]

# ---------- Daily Prayer for Individuals and Families (LSB pp. 294-298) ----------

BLESS_THE_LORD = V(['Let us bless the Lord.', '**Thanks be to God.**'], plain=True, citation='[Psalm 103:1]')
PRAYERS_FOR_OTHERS = [R('Prayers for others and ourselves'), WEEKDAY()]

daily_prayer_morning = [
    H('Daily Prayer: Morning'),
    SUB('For Individuals and Families'),
    R('These brief services are intended as a simple form of daily prayer for individuals and families, and in '
      'other settings.'),
    R('When more than one person is present, the versicles and responses may be spoken responsively, with one '
      'person reading the words in regular type and the others responding with the words in bold type. '
      'Prayers that are in bold type are to be prayed by all.'),
    R('For the readings, several verses have been recommended for each particular time of day. These may be '
      'used on a rotating basis. The value in using these few texts lies in the opportunity to learn them '
      'well. For those desiring a more complete selection of readings, the daily lectionary may be followed. '
      'Readings from the Small Catechism may also be incorporated into the services.'),
    R('In the prayers “for others and ourselves,” the following suggestions may be used to establish a '
      'pattern of daily and weekly prayer.'),
    COLS(WEEKDAY_TOPICS),
    SH('MORNING'),
    *INVOCATION,
    V(['In the morning, O Lord, You hear my voice;',
       '**in the morning I prepare a sacrifice for You and watch.**'], plain=True, citation='Psalm 5:3'),
    V(['My mouth is filled with Your praise,', '**and with Your glory all the day.**'], plain=True,
      citation='Psalm 71:8'),
    V(['O Lord, open my lips,', '**and my mouth will declare Your praise.**'], plain=True,
      citation='Psalm 51:15'),
    GLORIA,
    R('A hymn, canticle, or psalm may be sung or spoken.'),
    R('An appointed reading or one of the following is read: Colossians 3:1–4; Exodus 15:1–11; Isaiah 12:1–6; '
      'Matthew 20:1–16; Mark 13:32–36; Luke 24:1–9; John 21:4–14; Ephesians 4:17–24; Romans 6:1–4.'),
    LECT('morning', 'lesson'),
    R('A portion of the Small or Large Catechism may be read.'),
    R('The Apostles’ Creed is confessed.'),
    APOSTLES_CREED,
    R('Lord’s Prayer'),
    LORDS_PRAYER,
    *PRAYERS_FOR_OTHERS,
    R('Concluding prayers:'),
    P('Almighty God, merciful Father, who created and completed all things, on this day when the work of our '
      'calling begins anew, we implore You to create its beginning, direct its continuance, and bless its end, '
      'that our doings may be preserved from sin, our life sanctified, and our work this day be well pleasing '
      'to You; through Jesus Christ, our Lord. **Amen.**'),
    LUTHER_MORNING,
    BLESS_THE_LORD,
    R('Then go joyfully to your work.'),
]

daily_prayer_noon = [
    H('Daily Prayer: Noon'),
    *INVOCATION,
    V(['Listen to my prayer, O God, do not ignore my plea;', '**hear me and answer me.**',
       'Evening, morning, and noon', '**I cry out in distress, and He hears my voice.**',
       'Cast your cares on the Lord and He will sustain you;', '**He will never let the righteous fall.**'],
      plain=True, citation='Psalm 55:1–2a, 17, 22 NIV'),
    GLORIA,
    R('A hymn, canticle, or psalm may be sung or spoken.'),
    R('An appointed reading or one of the following is read: 1 Corinthians 7:17a, 23–24; Luke 23:44–46; '
      'Matthew 5:13–16; Matthew 13:1–9, 18–23; Mark 13:24–27; John 15:1–9; Romans 7:18–25; Romans 12:1–2; '
      '1 Peter 1:3–9; Revelation 7:13–17.'),
    LECT('midday', 'lesson'),
    V(['O Lord,', '**have mercy upon us.**', 'O Christ,', '**have mercy upon us.**', 'O Lord,',
       '**have mercy upon us.**'], plain=True, citation='Mark 10:47'),
    R('Lord’s Prayer'),
    LORDS_PRAYER,
    *PRAYERS_FOR_OTHERS,
    R('Concluding prayer:'),
    P('Blessed Lord Jesus Christ, at this hour You hung upon the cross, stretching out Your loving arms to '
      'embrace the world in Your death. Grant that all people of the earth may look to You and see their '
      'salvation; for Your mercy’s sake we pray. **Amen.**'),
    P('Heavenly Father, send Your Holy Spirit into our hearts to direct and rule us according to Your will, to '
      'comfort us in all our afflictions, to defend us from all error, and to lead us into all truth; through '
      'Jesus Christ, our Lord. **Amen.**'),
    BLESS_THE_LORD,
]

daily_prayer_evening = [
    H('Daily Prayer: Early Evening'),
    *INVOCATION,
    R('A candle may be lighted.'),
    V(['Let my prayer rise before You as incense,', '**the lifting up of my hands as the evening sacrifice.**'],
      plain=True, citation='Psalm 141:2'),
    V(['Joyous light of glory:', 'of the immortal Father;', 'heavenly, holy, blessed Jesus Christ.',
       'We have come to the setting of the sun,', 'and we look to the evening light.',
       'We sing to God, the Father, Son, and Holy Spirit:',
       'You are worthy of being praised with pure voices forever.',
       'O Son of God, O Giver of life: the universe proclaims Your glory.']),
    R('A hymn, canticle, or psalm may be sung or spoken.'),
    R('An appointed reading or one of the following is read: Luke 24:28–31; Exodus 16:11–21, 31; Isaiah 25:6–9; '
      'Matthew 14:15–21; Matthew 27:57–60; Luke 14:15–24; John 6:25–35; John 10:7–18; Ephesians 6:10–18a.'),
    LECT('evening', 'lesson'),
    R('A portion of the Small or Large Catechism may be read.'),
    R('Lord’s Prayer'),
    LORDS_PRAYER,
    *PRAYERS_FOR_OTHERS,
    R('Concluding prayer:'),
    P('Lord Jesus, stay with us, for the evening is at hand and the day is past. Be our constant companion on '
      'the way, kindle our hearts, and awaken hope among us, that we may recognize You as You are revealed in '
      'the Scriptures and in the breaking of the bread. Grant this for Your name’s sake. **Amen.**'),
    BLESS_THE_LORD,
    SH('MEALTIME PRAYERS'),
    R('Asking a blessing before the meal'),
    P('**Lord God, heavenly Father, bless us and these Your gifts which we receive from Your bountiful '
      'goodness, through Jesus Christ, our Lord. Amen.**', 'Small Catechism'),
    R('Returning thanks after the meal'),
    P('**We thank You, Lord God, heavenly Father, for all Your benefits, through Jesus Christ, our Lord, who '
      'lives and reigns with You and the Holy Spirit forever and ever. Amen.**', 'Small Catechism'),
]

daily_prayer_close = [
    H('Daily Prayer: Close of the Day'),
    *INVOCATION,
    V(['The Lord Almighty grant us a quiet night and peace at the last.', '**Amen.**'], plain=True),
    V(['It is good to give thanks to the Lord,', '**to sing praise to Your name, O Most High;**',
       'To herald Your love in the morning,', '**Your truth at the close of the day.**'], plain=True,
      citation='Psalm 92:1–2'),
    R('An appointed reading or one of the following is read: Matthew 11:28–30; Micah 7:18–20; '
      'Matthew 18:15–35; Matthew 25:1–13; Luke 11:1–13; Luke 12:13–34; Romans 8:31–39; '
      '2 Corinthians 4:16–18; Revelation 21:22—22:5.'),
    R('The Apostles’ Creed is confessed.'),
    APOSTLES_CREED,
    V(['Lord, now You let Your servant go in peace;', 'Your word has been fulfilled.',
       'My own eyes have seen the salvation', 'which You have prepared in the sight of every people:',
       'a light to reveal You to the nations', 'and the glory of Your people Israel.'],
      citation='Luke 2:29–32'),
    GLORIA,
    R('Lord’s Prayer'),
    LORDS_PRAYER,
    *PRAYERS_FOR_OTHERS,
    R('Concluding prayers:'),
    P('Visit our dwellings, O Lord, and in Your great mercy defend us from all perils and dangers of this night; '
      'for the love of Your only Son, our Savior Jesus Christ. **Amen.**'),
    LUTHER_EVENING,
    BLESS_THE_LORD,
    R('Then go to sleep at once and in good cheer.'),
]

responsive_prayer_1 = [
    H('Responsive Prayer 1'),
    SUB('Suffrages'),
    R('This order may be used in the morning or in the evening.'),
    L('Lord, have mercy upon us.'),
    C('Christ, have mercy upon us. Lord, have mercy upon us.'),
    LORDS_PRAYER,
    APOSTLES_CREED,
    L('I said, Lord, be merciful to me;'),
    C('heal my soul, for I have sinned against You.', 'Psalm 41:4'),
    L('Return, O Lord! How long?'),
    C('Have pity on Your servants!', 'Psalm 90:13'),
    L('Let Your steadfast love, O Lord, be upon us,'),
    C('even as we hope in You.', 'Psalm 33:22'),
    L('Let Your priests be clothed with righteousness,'),
    C('and let Your saints shout for joy.', 'Psalm 132:9'),
    L('O Lord, save Your people and bless Your heritage;'),
    C('be their shepherd and carry them forever.', 'Psalm 28:9'),
    L('Remember Your congregation,'),
    C('which You have purchased of old.', 'Psalm 74:2'),
    L('Peace be within your walls'),
    C('and security within your towers!', 'Psalm 122:7'),
    L('Let us pray for the faithful departed.'),
    C('Blessed are the dead who die in the Lord from now on.', 'Revelation 14:13'),
    L('Create in me a clean heart, O God,'),
    C('and renew a right spirit within me.', 'Psalm 51:10'),
    L('Cast me not away from Your presence,'),
    C('and take not Your Holy Spirit from me.', 'Psalm 51:11'),
    L('Restore to me the joy of Your salvation,'),
    C('and uphold me with a willing spirit.', 'Psalm 51:12'),
    L('O Lord, hear my prayer.'),
    C('And let my cry come to You.', 'Psalm 102:1'),
    L('Let us pray.'),
    R('In the morning'),
    COLLECT_FOR_GRACE,
    R('In the evening'),
    COLLECT_AGAINST_PERILS,
    *BENEDICAMUS,
    *BENEDICTION_TRINITY,
]

responsive_prayer_2 = [
    H('Responsive Prayer 2'),
    R('This order may be used at any time of day, especially for intercession.'),
    L('Lord, have mercy.'),
    C('Christ, have mercy. Lord, have mercy.'),
    LORDS_PRAYER,
    L('Show us Your steadfast love, O Lord,'),
    C('and grant us Your salvation.', 'Psalm 85:7'),
    L('Hear my prayer, O Lord;'),
    C('let my cry come to You.', 'Psalm 102:1'),
    SH('PRAYERS'),
    R('Prayers for the Church, the world, and those in need may be offered, each concluded:'),
    L('Lord, in Your mercy,'),
    C('hear our prayer.'),
    P('For the Church: Almighty God, grant to Your Church Your Holy Spirit and the wisdom that comes down from '
      'above, that Your Word may not be bound but have free course and be preached to the joy and edifying '
      'of Christ’s holy people; through Jesus Christ, our Lord. **Amen.**'),
    P('For those in need: Almighty and everlasting God, the comfort of the sad and the strength of those who '
      'suffer, let the prayers of Your children who cry out of any trouble come to You, that in every '
      'necessity they may rejoice to find Your mercy present with them; through Jesus Christ, our Lord. '
      '**Amen.**'),
    L('Let us bless the Lord.'),
    C('Thanks be to God.'),
    L('The Lord bless us, defend us from all evil, and bring us to everlasting life.'),
    C('Amen.'),
]

litany = [
    H('The Litany'),
    L('O Lord,'),
    C('have mercy.'),
    L('O Christ,'),
    C('have mercy.'),
    L('O Lord,'),
    C('have mercy.'),
    L('O Christ,'),
    C('hear us.'),
    L('God the Father in heaven,'),
    C('have mercy.'),
    L('God the Son, Redeemer of the world,'),
    C('have mercy.'),
    L('God the Holy Spirit,'),
    C('have mercy.'),
    L('Be gracious to us.'),
    C('Spare us, good Lord.'),
    L('Be gracious to us.'),
    C('Help us, good Lord.'),
    L('From all sin, from all error, from all evil; from the crafts and assaults of the devil; from sudden '
      'and evil death; from pestilence and famine; from war and bloodshed; from sedition and from rebellion; '
      'from lightning and tempest; from all calamity by fire and water; and from everlasting death:'),
    C('Good Lord, deliver us.'),
    L('By the mystery of Your holy incarnation; by Your holy nativity; by Your baptism, fasting, and '
      'temptation; by Your agony and bloody sweat; by Your cross and passion; by Your precious death and '
      'burial; by Your glorious resurrection and ascension; and by the coming of the Holy Spirit, the '
      'Comforter:'),
    C('Help us, good Lord.'),
    L('In all time of our tribulation; in all time of our prosperity; in the hour of death; and in the day of '
      'judgment:'),
    C('Help us, good Lord.'),
    L('We poor sinners implore You'),
    C('to hear us, O Lord.'),
    L('To rule and govern Your holy Christian Church; to preserve all pastors and ministers of Your Church in '
      'the true knowledge and understanding of Your wholesome Word and to sustain them in holy living; to put '
      'an end to all schisms and causes of offense; to bring into the way of truth all who have erred and are '
      'deceived; to beat down Satan under our feet; to send faithful laborers into Your harvest; and to '
      'accompany Your Word with Your grace and Spirit:'),
    C('We implore You to hear us, good Lord.'),
    L('To raise up those who fall and to strengthen those who stand; and to comfort and help the weakhearted '
      'and the distressed:'),
    C('We implore You to hear us, good Lord.'),
    L('To give to all peoples concord and peace; to preserve our land from discord and strife; to give our '
      'country Your protection in every time of need; to direct and defend all who are in authority; to bless '
      'and protect our magistrates and all our people; to watch over and help all who are in danger, '
      'necessity, and tribulation; to protect and guide all who travel; to grant all women with child, and '
      'all mothers with infant children, increasing happiness in their blessings; to defend all orphans and '
      'widows and provide for them; to strengthen and keep all sick persons and young children; to free those '
      'in bondage; and to have mercy on us all:'),
    C('We implore You to hear us, good Lord.'),
    L('To forgive our enemies, persecutors, and slanderers and to turn their hearts; to give and preserve for '
      'our use the kindly fruits of the earth; and graciously to hear our prayers:'),
    C('We implore You to hear us, good Lord.'),
    L('Lord Jesus Christ, Son of God,'),
    C('we implore You to hear us.'),
    L('Christ, the Lamb of God, who takes away the sin of the world,'),
    C('have mercy.'),
    L('Christ, the Lamb of God, who takes away the sin of the world,'),
    C('have mercy.'),
    L('Christ, the Lamb of God, who takes away the sin of the world,'),
    C('grant us Your peace.'),
    L('O Christ,'),
    C('hear us.'),
    L('O Lord,'),
    C('have mercy.'),
    L('O Christ,'),
    C('have mercy.'),
    L('O Lord,'),
    C('have mercy. Amen.'),
    LORDS_PRAYER,
    L('O Lord, deal not with us according to our sins'),
    C('nor reward us according to our iniquities.', 'Psalm 103:10'),
    L('Let us pray.'),
    P('Almighty God, merciful Father, You do not despise the sighing of a contrite heart nor the desire of '
      'those who are sorrowful. Mercifully assist our prayers that we make before You in all our troubles and '
      'adversities whenever they oppress us, that the evils which the craft and subtlety of the devil or man '
      'work against us be brought to nothing and by the providence of Your goodness they may be dispersed, '
      'that we, Your servants, being hurt by no persecutions, may evermore give thanks to You in Your holy '
      'Church; through Jesus Christ, Your Son, our Lord, who lives and reigns with You and the Holy Spirit, '
      'one God, now and forever. **Amen.**'),
]

prayers = [
    H('Prayers, Intercessions, and Thanksgivings'),
    R('These prayers may be used in the offices where “other prayers” or “prayers for others and ourselves” '
      'are indicated.'),
    H('The Church and Her Mission'),
    SH('FOR THE CHURCH'),
    P('Merciful God, we humbly implore You to cast the bright beams of Your light upon Your Church that we, '
      'being instructed by the doctrine of the blessed apostles, may walk in the light of Your truth and '
      'finally attain to the light of everlasting life; through Jesus Christ, our Lord. **Amen.**'),
    P('Almighty God, grant to Your Church Your Holy Spirit and the wisdom that comes down from above, that '
      'Your Word may not be bound but have free course and be preached to the joy and edifying of Christ’s '
      'holy people, that in steadfast faith we may serve You and, in the confession of Your name, abide unto '
      'the end; through Jesus Christ, our Lord. **Amen.**'),
    SH('FOR THE MISSION OF THE CHURCH'),
    P('Almighty God, You have called Your Church to witness that in Christ You have reconciled us to Yourself. '
      'Grant that by Your Holy Spirit we may proclaim the good news of Your salvation so that all who hear it '
      'may receive the gift of salvation; through Jesus Christ, our Lord. **Amen.**'),
    SH('FOR THOSE OUTSIDE THE CHURCH'),
    P('Almighty and everlasting God, You desire not the death of a sinner but that all would repent and live. '
      'Hear our prayers for those outside the Church. Take away their iniquity, and turn them from their false '
      'gods to You, the living and true God. Gather them into Your holy Church to the glory of Your name; '
      'through Jesus Christ, our Lord. **Amen.**'),
    SH('DEFENDING THE CHURCH FROM ERROR'),
    P('Almighty and everlasting God, You would have all to be saved and to come to the knowledge of the truth. '
      'By Your almighty power and unsearchable wisdom break and hinder all the counsels of those who hate Your '
      'Word and who, by corrupt teaching, would destroy it. Enlighten them with the knowledge of Your glory '
      'that they may know the riches of Your heavenly grace and, in peace and righteousness, serve You, the '
      'only true God; through Jesus Christ, our Lord. **Amen.**'),
]

SECTIONS = [
    ('matins', 'Matins', 219, matins),
    ('vespers', 'Vespers', 229, vespers),
    ('morning-prayer', 'Morning Prayer', 235, morning_prayer),
    ('evening-prayer', 'Evening Prayer', 243, evening_prayer),
    ('compline', 'Compline', 253, compline),
    ('responsive-prayer-1', 'Responsive Prayer 1', 282, responsive_prayer_1),
    ('responsive-prayer-2', 'Responsive Prayer 2', 285, responsive_prayer_2),
    ('litany', 'The Litany', 288, litany),
    ('daily-prayer-morning', 'Daily Prayer: Morning', 295, daily_prayer_morning),
    ('daily-prayer-noon', 'Daily Prayer: Noon', 296, daily_prayer_noon),
    ('daily-prayer-evening', 'Daily Prayer: Early Evening', 297, daily_prayer_evening),
    ('daily-prayer-close', 'Daily Prayer: Close of the Day', 298, daily_prayer_close),
    ('prayers', 'Prayers and Intercessions', 305, prayers),
]


def main():
    out = [{'id': sid, 'title': title, 'printedPage': page, 'blocks': blocks}
           for sid, title, page, blocks in SECTIONS]
    path = ROOT / 'app/src/data/content.json'
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'{len(out)} sections, {sum(len(s["blocks"]) for s in out)} blocks -> {path}')


if __name__ == '__main__':
    main()
