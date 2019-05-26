

# 品种，期限，主力，次新
debt_info = {
    'ND' : {
        '10' : ['180019.IB','180011.IB'],
        '7' : ['180013.IB'],
        '5' : ['180023.IB','180016.IB'],
        '3' : ['180015.IB'],
    },
    'NDD':{
        '10' : ['180210.IB','180205.IB'],
        '7' : ['180214.IB','180206.IB'],
        '5' : ['180211.IB','180204.IB'],
        '3' : ['180212.IB','180208.IB'],
    },
    'ADD' : {
        '10' : ['180406.IB']
    },
    'EID':{
        '5' : ['180309.IB'],
        '3' : ['180313.IB']
    },
    'NDF':{
        'T' : ['T1903.ZJ'],
        'TF' : ['TF1903.ZJ'],
        'TS' : ['TS1903.ZJ']
    }
}

debt_map = {
    'NDF-ND' : {
        ('NDF_10_M','ND_10_M') : (debt_info['NDF']['T'][0] , debt_info['ND']['10'][0]) if len(debt_info['NDF']['T'])>0 and len(debt_info['ND']['10'])>0 else -1,
        ('NDF_5_M','ND_5_M') : (debt_info['NDF']['TF'][0] , debt_info['ND']['5'][0]) if len(debt_info['NDF']['TF'])>0 and len(debt_info['ND']['5'])>0 else -1,
        ('NDF_3_M','ND_3_M') : (debt_info['NDF']['TS'][0] , debt_info['ND']['3'][0]) if len(debt_info['NDF']['TS'])>0 and len(debt_info['ND']['3'])>0 else -1,
        ('ND_10_M','ND_10_S') : (debt_info['ND']['10'][0] , debt_info['ND']['10'][1]) if len(debt_info['ND']['10'])==2 else -1,
        ('ND_7_M','ND_7_S') : (debt_info['ND']['7'][0] , debt_info['ND']['7'][1]) if len(debt_info['ND']['7'])==2 else -1,
        ('ND_5_M','ND_5_S') : (debt_info['ND']['5'][0] , debt_info['ND']['5'][1]) if len(debt_info['ND']['5'])==2 else -1,
        ('ND_3_M', 'ND_3_S') : (debt_info['ND']['3'][0] , debt_info['ND']['3'][1]) if len(debt_info['ND']['3'])==2 else -1,
    },
    'NDF-NDD' : {
        ('NDF_10_M','NDD_10_M') : (debt_info['NDF']['T'][0] , debt_info['NDD']['10'][0]) if len(debt_info['NDF']['T'])>0 and len(debt_info['NDD']['10'])>0 else -1,
        ('NDF_5_M','NDD_5_M') : (debt_info['NDF']['TF'][0] , debt_info['NDD']['5'][0]) if len(debt_info['NDF']['TF'])>0 and len(debt_info['NDD']['5'])>0 else -1,
        ('NDF_3_M','NDD_3_M') : (debt_info['NDF']['TS'][0] , debt_info['NDD']['3'][0]) if len(debt_info['NDF']['TS'])>0 and len(debt_info['NDD']['3'])>0 else -1,
        ('NDD_10_M','NDD_10_S') : (debt_info['NDD']['10'][0] , debt_info['NDD']['10'][1]) if len(debt_info['NDD']['10'])==2 else -1,
        ('NDD_7_M','NDD_7_S') : (debt_info['NDD']['7'][0] , debt_info['NDD']['7'][1]) if len(debt_info['NDD']['7'])==2 else -1,
        ('NDD_5_M','NDD_5_S') : (debt_info['NDD']['5'][0] , debt_info['NDD']['5'][1]) if len(debt_info['NDD']['5'])==2 else -1,
        ('NDD_3_M','NDD_3_S') : (debt_info['NDD']['3'][0] , debt_info['NDD']['3'][1]) if len(debt_info['NDD']['3'])==2 else -1,
    },
    'NDD-ND|ADD|EID' : {
        # 国开债-国债
        ('NDD_10_M','ND_10_M') : (debt_info['NDD']['10'][0] , debt_info['ND']['10'][0]) if len(debt_info['NDD']['10'])>0 and len(debt_info['ND']['10'])>0 else -1,
        ('NDD_5_M','ND_5_M') : (debt_info['NDD']['5'][0] , debt_info['ND']['5'][0]) if len(debt_info['NDD']['5'])>0 and len(debt_info['ND']['5'])>0 else -1,
        ('NDD_3_M','ND_3_M') : (debt_info['NDD']['3'][0] , debt_info['ND']['3'][0]) if len(debt_info['NDD']['3'])>0 and len(debt_info['ND']['3'])>0 else -1,

        # 国开债-农发债
        ('NDD_10_M','ADD_10_M') : (debt_info['NDD']['10'][0] , debt_info['ADD']['10'][0]) if len(debt_info['NDD']['10'])>0 and len(debt_info['ADD']['10'])>0 else -1,
        
        # 国开债-口行债
        ('NDD_5_M','EID_5_M') : (debt_info['NDD']['5'][0] , debt_info['EID']['5'][0]) if len(debt_info['NDD']['5'])>0 and len(debt_info['EID']['5'])>0 else -1,
        ('NDD_3_M','EID_3_M') : (debt_info['NDD']['3'][0] , debt_info['EID']['3'][0]) if len(debt_info['NDD']['3'])>0 and len(debt_info['EID']['3'])>0 else -1,
    },
    'period' : {
        # 国债不同期限
        ('ND_7_M','ND_10_M') : (debt_info['ND']['7'][0] , debt_info['ND']['10'][0]) if len(debt_info['ND']['7'])>0 and len(debt_info['ND']['10'])>0 else -1,
        ('ND_5_M','ND_10_M', 2, 1) : (debt_info['ND']['5'][0] , debt_info['ND']['10'][0]) if len(debt_info['ND']['5'])>0 and len(debt_info['ND']['10'])>0 else -1,
        ('ND_3_M','ND_5_M', 2, 1) : (debt_info['ND']['3'][0] , debt_info['ND']['5'][0]) if len(debt_info['ND']['3'])>0 and len(debt_info['ND']['5'])>0 else -1,

        # 国开债不同期限
        ('NDD_7_M','NDD_10_M') : (debt_info['NDD']['7'][0] , debt_info['NDD']['10'][0]) if len(debt_info['NDD']['7'])>0 and len(debt_info['NDD']['10'])>0 else -1,
        ('NDD_5_M','NDD_10_M', 2, 1) : (debt_info['NDD']['5'][0] , debt_info['NDD']['10'][0]) if len(debt_info['NDD']['5'])>0 and len(debt_info['NDD']['10'])>0 else -1,
        ('NDD_3_M','NDD_5_M', 2, 1) : (debt_info['NDD']['3'][0] , debt_info['NDD']['5'][0]) if len(debt_info['NDD']['3'])>0 and len(debt_info['NDD']['5'])>0 else -1,
    }

}


debt_name_trans = {
    'ND':'国债',
    'NDD':'国开债',
    'EID':'口行债',
    'ADD':'农发债',
    'NDF':'国债期货',
    'M':'主力',
    'S':'次新'
}


