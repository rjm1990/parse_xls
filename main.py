import pandas as pd
import re

"""
postgresql 解析xls文件，转换成建表语句

第一行：列名
第二行：中文注释
第三行：字段类型和长度
"""

def change_word(word):
    """
    第一个字母变小写，中间大写字母变_+小写
    :param word:
    :return:
    """
    if word == 'ID':
        return 'id'
    if 'AIID' in word or 'ARWID' in word or 'ARID' in word:
        return word.lower()
    word = re.sub('(?<!^)(?=[A-Z])', '_', word).lower()

    return word

def change_type(param):
    """
    String(2147483647) ->varchar(0)
    String(17)->varchar(17)
    Integer(4) -> int4
    Double(8) ->float8
    SmallInteger(2) ->int2
    :param param:
    :return:
    """
    if param == 'String(2147483647)':
        return 'varchar(5000)'
    if 'String' in param:
        return param.replace('String','varchar')
    if 'Integer' in param:
        return 'int4'
    if 'Double' in param:
        return 'float8'
    if 'SmallInteger' in param:
        return 'int2'

def assemble_sql(word, type, comment,table_name):

    sql = """
    ALTER TABLE "public"."{table_name}" ADD COLUMN {word} {type};
    comment on column "public"."{table_name}"."{word}" is '{comment}';
    """.format(table_name=table_name,word = word,type = type,comment = comment)

    return sql

def create_table(table_name, table_comment):
    """
    创建表，增加主键id（名字取单词首字母）
    表注释
    :param table_name:
    :param table_comment:
    :return:
    """
    pri_id = ''
    for i in table_name.split("_"):
        pri_id = pri_id + i[0]
    pri_id = pri_id+'_id'

    sql = """
    CREATE TABLE IF NOT EXISTS "public"."{table_name}" (
    "{pri_id}" varchar(32) COLLATE "pg_catalog"."default" NOT NULL,
    CONSTRAINT "{table_name}_copy1_pkey" PRIMARY KEY ("{pri_id}"));
    COMMENT ON TABLE "public"."{table_name}" IS '{table_comment}';
    """.format(table_name = table_name,pri_id = pri_id,table_comment = table_comment)

    return sql

def add_common_field(table_name):
    sql = """
    ALTER TABLE "public"."{table_name}" ADD COLUMN create_user VARCHAR ( 32 );
    comment on column "public"."{table_name}"."create_user" is '创建人';
    ALTER TABLE "public"."{table_name}" ADD COLUMN create_time TIMESTAMP;
    comment on column "public"."{table_name}"."create_time" is '创建时间';
    ALTER TABLE "public"."{table_name}" ADD COLUMN update_user VARCHAR ( 32 );
    comment on column "public"."{table_name}"."update_user" is '修改人';
    ALTER TABLE "public"."{table_name}" ADD COLUMN update_time TIMESTAMP;
    comment on column "public"."{table_name}"."update_time" is '修改时间';
    ALTER TABLE "public"."{table_name}" ADD COLUMN del_flag CHAR ( 1 );
    comment on column "public"."{table_name}"."del_flag" is '0正常1删除';
    ALTER TABLE "public"."{table_name}" ADD COLUMN province VARCHAR ( 100 );
    comment on column "public"."{table_name}"."province" is '省';
    ALTER TABLE "public"."{table_name}" ADD COLUMN city VARCHAR ( 100 );
    comment on column "public"."{table_name}"."city" is '市';
    ALTER TABLE "public"."{table_name}" ADD COLUMN county VARCHAR ( 100 );
    comment on column "public"."{table_name}"."county" is '县';
    ALTER TABLE "public"."{table_name}" ADD COLUMN geom geometry(GEOMETRY);
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends1 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends2 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends3 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends4 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends5 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends6 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends7 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends8 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends9 VARCHAR ( 255 );
    ALTER TABLE "public"."{table_name}" ADD COLUMN extends10 VARCHAR ( 255 );
    """.format(table_name = table_name)
    return sql

def trans(table_name,table_comment,file_path):
    #创建表
    create_sql = create_table(table_name,table_comment)
    print(create_sql)
    #读取文件
    df = pd.read_excel(file_path)
    #获取所有列
    col = df.columns.values
    df_arr = df.values
    index = 0
    for i in col:
        word = i.strip()
        if word == 'TitleLine': #结束标识
            break
        word = change_word(word) #字段名
        type = change_type(df_arr[1][index]) #字段类型
        comment = df_arr[0][index] #字段注释
        field_sql = assemble_sql(word,type,comment,table_name)
        print(field_sql)
        index += 1
    #增加公共字段
    common_sql = add_common_field(table_name)
    print(common_sql)

if __name__ == '__main__':

    file_path = '\A1_InvestigationRegion\MainAFSvyRegion-主要活动断层制图区-面.xls'

    trans('hddc_main_afsvy_region','主要活动断层制图区-面',file_path)