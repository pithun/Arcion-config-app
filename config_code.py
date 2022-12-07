import streamlit as st
import re

# from PIL import Image
# image = Image.open('arcion.jfif')

# st.image(image)

st.title('Welcome to the Arcion Config app 💻')

db_name = st.text_input('Enter Database name')
table_names = st.file_uploader('Upload a .csv file containing table names', type=['csv', 'txt'])

text = 'allow:' + '\n' + '- schema : "' + db_name + '"\n' + '  types: [TABLE, VIEW]' + '\n' + '  allow:'

if table_names is not None:
    reading = str(table_names.read(), "utf-8")
    reading = re.findall(r'\w+', reading)[1:]
    with st.expander('Expand to download the filter file'):
        for table in reading:
            text += '\n' + '     ' + table + ':'

        st.download_button('Click to Download', data=text, file_name='filter.yaml')

    # Extractor configuration section.
    with st.expander('Expand to configure the extractor file'):
        option = st.selectbox(
            'Please select what mode you\'re running replicant',
            ('snapshot', 'delta-snapshot'))

        extractor = open('support_files/extractor.txt', 'r')
        read_extractor = extractor.read()
        if option == 'snapshot':
            st.write('Extractor configuration is not necessary for ' + option + 'mode, use the default config file.')
            pass
        else:
            read_extractor += '- schema: "' + db_name + '"\n    tables: \n      '
            for tab_id, each_table in enumerate(reading):
                st.write('For table ' + each_table)
                col1, col2 = st.columns(2)

                with col1:
                    snapshot_keys = st.text_input(
                        'Enter the Delta Snapshot Key(s)', placeholder='e.g Delta_ID, Delta_Primary',
                        key=tab_id + len(reading) + 0.1628)

                with col2:
                    row_id_keys = st.text_input(
                        'Enter the row identifier Key(s) ', placeholder='e.g row_ID, row_Primary',
                        key=tab_id + len(reading) + 1.9955)

                read_extractor += each_table + ':\n        delta-snapshot-keys: [' + \
                                  snapshot_keys + ']\n        row-identifier-key: [' \
                                  + row_id_keys + '] \n      '
                snapshot_keys = ''
                row_id_keys = ''
                if tab_id + 1 < len(reading) and st.checkbox('Go to Next table', key=tab_id):
                    pass
                else:
                    break
            st.download_button('Generate Extractor', data=read_extractor, file_name='extractor.yaml')

    # Applier configuration section.
    with st.expander('Expand to configure applier file'):
        applier = open('support_files/applier.txt', 'r')
        read_applier = applier.read()
        read_applier += '    - catalog: "' + db_name + '"\n      tables: \n      '
        remaining_applier = open('support_files/remaining_applier.txt', 'r').read()
        for tab_id, each_table in enumerate(reading):
            st.write('For table ' + each_table)
            col1, col2 = st.columns(2)
            col3, col4 = st.columns(2)

            with col1:
                table_store = st.radio(
                    'Pick an SS table store', ['ROW', 'COLUMN'], key=tab_id + len(reading) + 0.00006, index=1)

            with col2:
                table_type = st.radio(
                    'Pick choose a table type', ['REGULAR', 'REFERENCE', 'TEMPORARY'],
                    key=tab_id + len(reading) + 0.0015)
            with col3:
                sort_keys = st.text_input(
                    'Enter the sort Key', placeholder='This is the key in which the column store table is '
                                                      'sorted on.',
                    key=tab_id + len(reading) + 0.001)

            with col4:
                shard_keys = st.text_input(
                    'Enter the shard Key', placeholder='This is the key in which our data is spread into partitions'
                                                       ' in the leaf nodes',
                    key=tab_id + len(reading) + 195)

            read_applier += each_table + ':\n          table-type: ' + \
                            table_type + '\n          table-store: ' \
                            + table_store + '\n          sort-key: [' + \
                            sort_keys + ']\n          shard-key: [' + \
                            shard_keys + ']\n      '

            table_store = ''
            table_type = ''
            sort_keys = ''
            shard_keys = ''
            if tab_id + 1 < len(reading) and st.checkbox('Go to Next table', key=tab_id + len(reading) + 0.0232):
                pass
            else:
                break
        read_applier += '\n'+remaining_applier
        st.download_button('Generate applier', data=read_applier, file_name='applier.yaml')

    # Generating the view command
    # we already have a syntax for replicant Id
    st.subheader('Generating the Replicant command')
    st.write('ID convention: Each ID is named repl_initials_of DB. For example the DB '
             'NeuronSTG_DEV will have repl_NSD.')

    # if st.checkbox('Manually specify'):

    # else:
    #   rep_id = 'repl_'+''.join(re.findall(r'[A-Z]', db_name))
    # st.write(''.join(re.findall(r'[A-Z]', db_name)))

    col5, col6 = st.columns(2)

    with col5:
        rep_id = st.text_input('Enter your desired ID')

    with col6:
        dir_name = st.text_input('Enter your parent directory name', placeholder='e.g "conf" in conf/conn/teradata.yaml')

    if st.button('Get Replicant run command'):
        rep = './bin/replicant '+ option +' '+ dir_name+ '/conn/teradata.yaml ' \
              +dir_name+'/conn/singlestore.yaml --filter filter/teradata_filter.yaml ' \
                        '--extractor '+ dir_name+ '/src/teradata.yaml ' \
                        '--applier '+ dir_name+ '/dst/singlestore.yaml --id ' + rep_id
        st.code(rep, language='python')

else:
    pass
