from fontTools.ttLib import TTFont


def modify_html(newFont, html):
    baseFont = TTFont(r'20ad699b.woff')
    uniList = newFont['cmap'].tables[0].ttFont.getGlyphOrder()
    numList = []
    baseNumList = ['3', '5', '8', '7', '0', '1', '9', '6', '2', '4']
    baseUniCode = ['uniF64E', 'uniF345', 'uniE8F8', 'uniEB4E', 'uniE261', 'uniECAE',
                   'uniE738', 'uniE492', 'uniE979', 'uniEB3D']

    for i in range(1, 12):
        newGlyph = newFont['glyf'][uniList[i]]
        for j in range(10):
            baseGlyph = baseFont['glyf'][baseUniCode[j]]
            if newGlyph == baseGlyph:
                numList.append(baseNumList[j])
                break
    rowList = []
    for i in uniList[2:]:
        i = i.replace('uni', '&#x').lower()
        rowList.append(i)
    dictory = dict(zip(rowList, numList))
    for key in dictory:
        if key in str(html):
            html = html.replace(key, str(dictory[key]))
    return html

if __name__ == '__main__':
    newFont=TTFont(r'20ad699b.woff')
    modify_html(newFont, '配送 ¥&#xf64e.&#xf345')

