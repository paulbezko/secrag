def save_file_contents(fpath, content, encoding, bom=None):
    with open(fpath, mode='w', encoding=encoding) as fout:
        if bom:
            fout.write(u'\ufeff')
        fout.write(content)
        print('Processed', fpath)

save_file_contents('requirements.txt', content, 'utf-16-LE', bom=True)