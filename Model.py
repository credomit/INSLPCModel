import re, sys, json, configparser,os
import sqlite3 as sql
from typing import Dict, Tuple
from PyQt5 import QtCore, QtGui, QtWidgets, uic,Qt
from PyQt5.QtChart import QPieSeries, QChart, QChartView
from .windows_creator import *
from .translator import translator
import notifiers
from pathlib import Path
from .preferences import *
import pyqtgraph as pg
import sys, random
from .styler import Styler
from pyqtgraph import QtCore as QtCoregraph
from pyqtgraph import QtGui as QtGuigraph
from types import MethodType
from .IN import *

def replace_variable_value(item, text):
    if text != '':
        re_text = eval(text)
        if type(re_text) in [list, tuple, set]:
            re_text = list(re_text)
            re_text = [ str(i) for i in  re_text ]
            re_text = ''.join(list(re_text))

    else:
        re_text = ''
    return re_text






class INSAPP(object):

    

    def __init__(self, app_name, app_version, translateable_labels_and_buttons,app_file_type, app_logo ,  preferences_call_btn = 'PREFERENCES_ACTION'):
        
        self.translateable_labels   = translateable_labels_and_buttons
        self.app_name               = app_name
        self.app_version            = app_version
        self.app_logo               = os.path.join(os.path.join(os.path.dirname( __file__ )),'..',app_logo)
        self.qss_style              = ''
        self.app_file_type          = app_file_type
        
        self.UI_file                = 'main.ui'
        self.pyqt5_app              = QtWidgets.QApplication(sys.argv)
        self.MainWindow             = QtWidgets.QMainWindow()
        self.UI                     = uic.loadUi(self.UI_file, self.MainWindow)
        self.UI.setWindowTitle(app_name)
        self.MainWindow.closeEvent = MethodType(self.closeEvent,self.MainWindow)
        
        
        

        
        self.translator             = translator(self)
        self.translate              = self.translator.translate
        self.preferences_call_btn   = getattr(self.UI, preferences_call_btn)
        self.preferences_call_btn.triggered.connect(lambda: open_preferences_window(self))
        self.Styler                 = Styler(self)
        
        
        
    def closeEvent(self,r, event):
            close = QtWidgets.QMessageBox.question(self.UI,
	                                         "QUIT",
	                                         self.translate(f'Are you sure want to close {self.app_name}?'),
	                                         QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No )
            if close == QtWidgets.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()

    def run(self):
        back_connections(self)
        INSCI(self)
        

        self.pyqt5_app.exec_()

    def run_main_window(self, LW): # LW : Loading Window
        step_value = int(100 / len(self.listed_items))
        
        for item in self.listed_items:
            LW.ui.progressBar.setValue(LW.ui.progressBar.value() + step_value)
            setattr(self, item.__name__ , item(INSApp = self ))
        
        LW.close()
        self.Styler.apply_style()
        self.UI.show()
        


class SubItem(object):
    def __init__(self, fields, model):
        self.model = model
        for var in fields.keys():
            setattr(self, var , fields[var] )
            
            if var in self.model.fields and self.model.fields[var].field_type == 'ManyToManyField':
                setattr(self, var+'_data' , [] )



class Item(object):

    

    def __init__(self, fields, model):
        self.model = model
        for var in fields.keys():
            setattr(self, var , fields[var] )
            
            if var in self.model.fields and self.model.fields[var].field_type == 'ManyToManyField':
                setattr(self, var+'_data' , fields[var] )
        



    def __str__(self):
        if self.model.custom_str != None:
            return self.model.custom_str(self)
        else:
            return replace_variable_value(self, self.model.view_name)


    def get(self, field):
        field_obj = getattr(self, field)
        return getattr(field_obj, field_obj.Get_UI_Value_Function )()

    def delete(self):
        ansower = QtWidgets.QMessageBox.question(self.model.INSApp.UI , self.model.INSApp.translate('Delete Confirm') , self.model.INSApp.translate('Are you sure do you want to delete')+' '+  str(self) +'?')

        if ansower==QtWidgets.QMessageBox.Yes:
            if self.model.before_delete==None or self.model.before_delete(self):
                db_connection = sql.connect(self.Model.INSApp.database_path)
                db_connection.execute(f''' DELETE from {self.Model.DBTableName} where id = {self.id} ''')
                db_connection.commit() 
                db_connection.close()
                item_data = vars(self)
                self.Model.objects.remove(self)
                
                self.model.ui_list.takeItem(self.model.ui_list.row(self.ui_obj))

                if self.on_delete != None:
                    self.on_delete(data = item_data)
                
        

    def save(self, call_on_edit = False, call_before_edit = False):
        
            

        db_connection = sql.connect(self.model.INSApp.database_path)

        #get old data as dict
        cursor        = db_connection.cursor()
        data          = cursor.execute(f'''SELECT * FROM {self.model.DBTableName}  where id = {self.id} ''')
        columns       = [ i[0] for i in data.description]
        old_data      = [ i for i in data ][0]
        old_data      = {columns[i]: old_data[i] for i in range(len(columns)) }

        

        new_data = {}
        for field in self.model.fields.keys():
            if field !=None :
                value =  getattr(self, field)

                if value == None:
                    value = '""'
                elif type(value) in [list, set, dict, tuple]:
                    if self.model.fields[field].field_type == 'ManyToManyField':
                        value =  getattr(self, field+'_data')
                    value = json.dumps(value)
                db_connection.execute(f''' UPDATE {self.model.DBTableName} set {field} = ? where id = {self.id} ''', [value,])
                new_data[field] = value

        if self.model.before_edit == None or (call_on_edit and self.model.before_edit(old_data = old_data, new_data = new_data)):
            db_connection.commit() 
            db_connection.close()
            
            self.ui_obj.setText(self.__str__())
            if self.model.on_edit != None and call_on_edit:
                self.model.on_edit(old_data = old_data, new_data = new_data )

            #update dashboard
            for mode in self.model.GRAPH_MODES:
                if getattr(self.model , "dashboard_frame_items_"+mode).currentData() == self:
                    
                    self.model.View_Graph(mode)
            
            for mode in self.model.PIE_GRAPH_MODES:
                if getattr(self.model , "dashboard_pie_items_"+mode).currentData() == self:
                    
                    self.model.View_Pie(mode)


            
            
            return True

        else:
            db_connection.close()
            return False
        
        


class Model(object):

    
    view_name           = ' f" {item.model.__class__.__name__} object ({item.id})"'
    tooltip             = ''
    add_conditions      = {}
    GRAPH_MODES         = []
    PIE_GRAPH_MODES     = []

    on_add              = None
    on_edit             = None
    on_delete           = None

    before_add          = None
    before_save         = None # before edit
    before_delete       = None

    search_bar          = None
    ui_list_info        = None
    filters             = None
    dashboard           = None
    custom_str          = None
    before_edit         = None

    def __init__(self, INSApp):
        
        #fields      = []
        self.objects     = []
        self.DBTableName = self.__class__.__name__
        
        self.INSApp      = INSApp
        self.check_db_table()
        self.create_items_objects()
        

        #connections
        if self.add_button != None:
            self.add_button.clicked.connect(lambda: create_item_window(self.INSApp, self))
            self.add_button.setText('')
            self.add_button.setIcon(self.INSApp.Styler.get_icon('add'))

        if self.delete_button != None:
            self.delete_button.clicked.connect(self.delete_selected)
            self.delete_button.setText('')
            self.delete_button.setIcon(self.INSApp.Styler.get_icon('delete'))
            self.delete_button.setProperty('btn_type','delete')

        if self.ui_list != None:
            self.ui_list.itemDoubleClicked.connect(edit_item_window)

        if self.search_bar != None:
            self.search_bar.textChanged.connect(self.search)
            fields_filters_text = [ f'@{f}:' for f in self.fields.keys() ]
            self.filters_compliter =  QCompleter(list(self.filters.keys()) + fields_filters_text )
            self.filters_compliter.setObjectName('Completer')
            self.filters_compliter.popup().setStyleSheet('background-color:rgba(0,0,0,0.6);color:rgb(225,225,225);')
            self.search_bar.setCompleter(self.filters_compliter)
            self.search_bar.setPlaceholderText(self.INSApp.translate('Search (Word, #, @)'))
        
        if self.ui_list_info != None:
            self.ui_list_info.setText(f'{len(self.objects)} item')

        if self.dashboard != None:
            self.dashboard.setWidgetResizable(True)
            self.dashboardAreaWidgetContents = QWidget()
            self.dashboardAreaWidgetContents.setObjectName(self.DBTableName+"dashboardAreaWidgetContents")
            self.dashboardAreaWidgetContents.setGeometry(QRect(0, 0, 868, 876))
            self.dashboardGridLayout = QGridLayout(self.dashboardAreaWidgetContents)
            self.dashboardGridLayout.setObjectName(self.DBTableName+"dashboardGridLayout")



            pg.setConfigOption('background', None)
            
            

            i = 0
            
            for mode in self.GRAPH_MODES:
                setattr(self, "dashboard_frame_"+mode, QFrame(self.dashboardAreaWidgetContents))
                frame = getattr(self, "dashboard_frame_"+mode)
                frame.setObjectName(mode+"_dashboard_frame_")
                frame.setProperty('frame_type', 'graph')

                frame.setMinimumSize(QSize(0, 282))
                frame.setFrameShape(QFrame.StyledPanel)

                setattr(self, "dashboard_frame_gridLayout_"+mode,QGridLayout(frame))
                dashboard_frame_gridLayout = getattr(self, "dashboard_frame_gridLayout_"+mode)
                dashboard_frame_gridLayout.setObjectName("dashboard_frame_gridLayout_"+mode)

                setattr(self, "dashboard_frame_graph_"+mode,pg.GraphicsWindow())
                graph = getattr(self, "dashboard_frame_graph_"+mode)
                graph.setObjectName(u"frame_"+mode)
                graph.setFrameShape(QFrame.StyledPanel)
                graph.setFrameShadow(QFrame.Raised)
                dashboard_frame_gridLayout.addWidget(graph, 2, 0, 1, 2)

                setattr(self, "dashboard_frame_items_"+mode, QComboBox(frame))
                items_combo = getattr(self, "dashboard_frame_items_"+mode)
                items_combo.setObjectName(u"comboBox")
                items_combo.setMaximumSize(QSize(175, 16777215))
                for item in self.objects: 
                    items_combo.addItem(str(item), item)

                setattr(self, "dashboard_frame_info_"+mode, QLabel(frame))
                info = getattr(self, "dashboard_frame_info_"+mode)
                info.setObjectName("label_info_"+mode)
                info.setText('')
                dashboard_frame_gridLayout.addWidget(info, 1, 1, 1, 2)

                if len(self.objects):
                    self.View_Graph(mode)
                    
                items_combo.currentIndexChanged.connect(partial(  self.View_Graph, mode ))

                dashboard_frame_gridLayout.addWidget(items_combo, 1, 0, 1, 1)

                setattr(self, "dashboard_frame_title_"+mode, QLabel(frame))
                label = getattr(self, "dashboard_frame_title_"+mode)
                label.setObjectName("label_title_"+mode)
                sizePolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(label.sizePolicy().hasHeightForWidth())
                label.setSizePolicy(sizePolicy)
                font = QFont()
                font.setPointSize(18)
                label.setFont(font)
                label.setText(mode.title())

                dashboard_frame_gridLayout.addWidget(label, 0, 0, 1, 2)
                self.dashboardGridLayout.addWidget(frame , i, 0, 1, 1)

                i+=1


            for mode in self.PIE_GRAPH_MODES:
                setattr(self, "dashboard_pie_frame_"+mode, QFrame(self.dashboardAreaWidgetContents))
                frame = getattr(self, "dashboard_pie_frame_"+mode)
                frame.setObjectName(mode+"dashboard_pie_frame_")
                frame.setProperty('frame_type', 'graph')
                

                
                frame.setFrameShape(QFrame.StyledPanel)

                setattr(self, "dashboard_pie_gridLayout_"+mode,QGridLayout(frame))
                dashboard_frame_gridLayout = getattr(self, "dashboard_pie_gridLayout_"+mode)
                dashboard_frame_gridLayout.setObjectName("dashboard_pie_gridLayout_"+mode)

                setattr(self, "dashboard_frame_pie_"+mode,QPieSeries())
                pie = getattr(self, "dashboard_frame_pie_"+mode)
                pie.setObjectName(u"frame_"+mode)

                chart = QChart()
                chart.addSeries(pie)
                chart.setAnimationOptions(QChart.SeriesAnimations)
                view_title = mode.replace('_', ' ').title()
                chart.setTitle(f'<span style=\"color: #ffffff;\">{ view_title }</span>')
                chart.setBackgroundVisible(False)

                chartview = QChartView(chart)
                chartview.setStyleSheet('color:white;')
                chartview.setMinimumSize(QSize(0, 482))

                setattr(self, "dashboard_pie_items_"+mode, QComboBox(frame))
                items_combo = getattr(self, "dashboard_pie_items_"+mode)
                items_combo.setObjectName(u"comboBox")
                items_combo.setMaximumSize(QSize(175, 16777215))
                for item in self.objects: 
                    items_combo.addItem(str(item), item)

                extra_fields_dict = self.PIE_GRAPH_MODES[mode]['extra_fields']

                field_index = 2
                for field in extra_fields_dict:
                    setattr(self, "dashboard_pie_extrafield_label_"+mode+'_'+field, QLabel(frame))
                    info = getattr(self, "dashboard_pie_extrafield_label_"+mode+'_'+field)
                    info.setObjectName("dashboard_pie_extrafield_label_"+mode+'_'+field)
                    info.setText(field)
                    dashboard_frame_gridLayout.addWidget(info, field_index, 0, 1, 1)
                    extra_fields_dict[field].view(self, self.INSApp.MainWindow, field, field_index,extra_fields_dict[field], field_gridLayout = dashboard_frame_gridLayout, view_on_main_window = True )
                    setattr(self, 'dashboard_pie_extrafield_'+mode+'_'+field, extra_fields_dict[field])
                    field_index+=1

                if field_index > 2:
                    setattr(self, "dashboard_pie_extrafield_apply_btn"+mode, QPushButton(frame))
                    apply_btn = getattr(self, "dashboard_pie_extrafield_apply_btn"+mode)
                    apply_btn.setObjectName("dashboard_pie_extrafield_apply_btn"+mode)
                    apply_btn.setText(self.INSApp.translate('APPLY'))
                    apply_btn.setStyleSheet('padding:8px;')
                    apply_btn.clicked.connect(partial(  self.View_Pie, mode ))
                    dashboard_frame_gridLayout.addWidget(apply_btn, field_index, 0, 1, 1)

                setattr(self, "dashboard_pie_info_"+mode, QLabel(frame))
                info = getattr(self, "dashboard_pie_info_"+mode)
                info.setObjectName("dashboard_pie_info_"+mode)
                info.setText('')

                if len(self.objects):
                    self.View_Pie(mode)
                    
                items_combo.currentIndexChanged.connect(partial(  self.View_Pie, mode ))

                dashboard_frame_gridLayout.addWidget(chartview, field_index+2, 0, 1, 5)
                dashboard_frame_gridLayout.addWidget(info,  field_index+3, 0, 1, 3)

                dashboard_frame_gridLayout.addWidget(items_combo, 1, 0, 1, 1)
                self.dashboardGridLayout.addWidget(frame , i, 0, 1, 1)

                i+=1

            self.dashboard.setProperty('frame_type', 'handler')
            self.dashboard.setWidget(self.dashboardAreaWidgetContents)
            frame.setStyleSheet(self.INSApp.currentStyle)



    def point_clicked(self, item, current_item):
        info_label      = getattr(self, "dashboard_frame_info_"+item.mode)
        info_label.setText(item.point_data[current_item[0].pos().x()])

    def View_Graph(self, mode):

        graph = getattr(self, "dashboard_frame_graph_"+mode)
        items_combo = getattr(self, "dashboard_frame_items_"+mode)
        
        
        graph_data = self.GRAPH_MODES[mode](items_combo.currentData())
        x       = graph_data['x'] 
        xdict   = dict(enumerate(graph_data['x-keys']))
        y       = graph_data['y']
        ydict   = dict(enumerate(graph_data['y-keys']))

        stringaxis = pg.AxisItem(orientation='bottom')
        stringaxis.setTicks([xdict.items()])

        stringaxis_y = pg.AxisItem(orientation='left')
        stringaxis_y.setTicks([ydict.items()])


        graph.clear()
        plot = graph.addPlot(axisItems={'bottom': stringaxis, 'left': stringaxis_y})
        plot.showGrid(x = True, y = True, alpha = 0.5)
        
        line = plot.plot(x,y,  symbol ='o', symbolPen ='g', symbolBrush = 1.5, name ='green', width = 1,  pen=pg.mkPen('g', width=2.5))

        line.installSceneEventFilter(plot)
        line.setAcceptHoverEvents(True)
        plot.setAcceptHoverEvents(True)
        line.sigPointsClicked.connect(self.point_clicked)
        line.mode           = mode
        line.main_plot      = plot
        line.stringaxis     = list(xdict)
        line.point_data     = graph_data['point-data']
        
    def View_Pie(self, mode):
        pie  = getattr(self, "dashboard_frame_pie_"+mode)
        items_combo = getattr(self, "dashboard_pie_items_"+mode)

        extra_fields_dict = self.PIE_GRAPH_MODES[mode]['extra_fields']
        extra_data = {}
        for field in extra_fields_dict:
            ui_field = getattr(self, 'dashboard_pie_extrafield_'+mode+'_'+field)
            extra_data[field] = ui_field.get_data()


        all_info = self.PIE_GRAPH_MODES[mode]['function'](items_combo.currentData(),extra_data )
        data = all_info['data']
        if all_info.get('extra_info') != None:
            info = getattr(self, "dashboard_pie_info_"+mode)
            info.setText(all_info.get('extra_info'))

        pie.clear()
        for a_slice in  data:
            sl = pie.append( a_slice , data[a_slice] )
            sl.setBorderWidth(1.5)
            sl.setBorderColor(QColor(200,200,200))

        for slice in pie.slices():
            oldLabel=slice.label()
            slice.setLabel(( f'<span style=\"color: #ffffff;\">{oldLabel}: %({slice.percentage()*100})</span>'))
        

        def s_hovered(pie, current_slice):
            for unhovered_slice  in pie.slices():
                if unhovered_slice != current_slice:
                    unhovered_slice.setExploded(False)
                    unhovered_slice.setLabelVisible(False)
            current_slice.setExploded(True)
            current_slice.setLabelVisible(True)
 	
        pie.hovered.connect(partial(s_hovered, pie))

 


    def search(self, text):
        self.ui_list.clear()
        filtered_objects = []
        if text != '':


            if text[0] =='#':#custom filters
                if text.split(':')[0]+':' in self.filters.keys():

                    if ':' in text : # have values
                        value = ':'.join(text.split(':')[1:])
                        filtered_objects = self.filters[text.split(':')[0]+':'](self, self.objects, value = value)
                    else:
                        filtered_objects = self.filters[text.split(':')[0]+':'](self, self.objects)


            elif text[0] =='@':#fields filters
                try:
                    field           = text[1:].split(':')[0]
                    field_value    = ':'.join(text[1:].split(':')[1:])
                    
                    for obj in self.objects:
                        if (self.fields[field].field_type == 'OneToOneField' and field_value in str(getattr(obj, field+'__obj'))) or field_value in str(getattr(obj, field)):
                            filtered_objects.append(obj)

                except:
                    pass

                
            else:
                text_words = set(text.split(' '))
                if '' in text_words:
                    text_words.remove('')

                for item_object in self.objects:
                    obj_data = list(vars(item_object).values())
                    for i in range(len(obj_data)):
                        if type(obj_data[i]) == dict:
                            obj_data[i] = ''
                            obj_data += [ str(b) for b in list(obj_data[i].values())]

                        elif type(obj_data[i]) in [list, set, tuple]:
                            if len(obj_data[i])>0:
                                if type(obj_data[i][0]) == dict:
                                    for item in obj_data[i]:
                                        obj_data[i] = ''
                                        obj_data += [ str(b) for b in list(item.values())]

                            else:
                                obj_data += [ str(b) for b in list(obj_data[i])]
                                    
                                obj_data[i] = ''

                        elif type(obj_data[i]) == str:
                            try:
                                bit = json.loads(obj_data[i])
                                if type(bit) == dict:
                                    obj_data += list(bit.values())
                                else:
                                    obj_data += list(bit)
                                obj_data[i] = ''
                            except:
                                pass
                        else:
                            obj_data[i] = str(obj_data[i])


                    
                    obj_words = set(' '.join(obj_data).split(' ')) #convert all data to words set
                    if text_words.issubset(obj_words):
                        filtered_objects.append(item_object)
                    
                    else:
                        ex_status = True
                        for word in text_words:
                            obj_words_str = [ str(i) for i in obj_words if type(i) in [float,bool,str,int,list, tuple, dict, set] ]
                            if word not in ' '.join(obj_words_str):
                                ex_status = False

                        if ex_status:
                            filtered_objects.append(item_object)


            for item_object in filtered_objects:
                self.add_item_to_list(item_object)
            self.ui_list_info.setText(f'{len(filtered_objects)}/{len(self.objects)} item found')
            
        else:
            for item_object in self.objects:
                self.add_item_to_list(item_object)
            self.ui_list_info.setText(f'{len(self.objects)} item')

        


    def check_db_table(self):
        db_connection = sql.connect(self.INSApp.database_path)
        tabels = db_connection.execute("SELECT name FROM sqlite_master WHERE type ='table'").fetchall()
        tabels = [ i[0] for i in tabels ]

        if not self.DBTableName in tabels:
            columns = ['id integer primary key autoincrement',]
            for field in self.fields.keys():
                columns.append(f'{field} { self.fields[field].data_base_type }')
            columns = ','.join(columns)
            db_connection.execute(f"create table { self.DBTableName } ({columns})")
        
        else:
            columns = ( bit[0] for bit in db_connection.execute(f'select * from {self.DBTableName}').description )
            new_Columns =  list(set(self.fields.keys()) - set(columns))
            for new_column in new_Columns:
                db_connection.execute(f"ALTER TABLE {self.DBTableName} ADD {new_column}")

            db_connection.commit()
        db_connection.close()

    def create_items_objects(self):

        db_connection = sql.connect(self.INSApp.database_path)
        columns = list(self.fields.keys())+['id',]
        str_columns = ','.join(columns)
        data = db_connection.execute(f"SELECT {str_columns} from {self.DBTableName} ").fetchall()
        
        
        for item in data:
            data = {}
            for i in range(len(item)):
                data[columns[i]] = item[i]
                if columns[i]!='id' :
                    if self.fields[columns[i]].field_type == 'OneToOneField':
                        try:
                            item_id = int(item[i])
                        except:
                            item_id = None
                        data[columns[i]+'__obj'] = getattr( self.INSApp, self.fields[columns[i]].model).get(id=item_id)
                        
                    elif self.fields[columns[i]].field_type == 'ManyToManyField':
                        try:
                            data[columns[i]] = json.loads(item[i].replace("'",'"'))
                        except:
                            pass

                    elif self.fields[columns[i]].field_type == 'BoolField':
                        if data[columns[i]] == 'False':
                            data[columns[i]] = 0
                        else:
                            data[columns[i]] = 1

                        data[columns[i]] = bool(int(data[columns[i]]))
                        
            data['view_name'] = self.view_name
            data['Model'] = self
            item_obj = Item(data, self)
            self.objects.append(item_obj)
            self.add_item_to_list( item_obj)

        db_connection.close()

    def add_item_to_list(self, obj):
        item = QtWidgets.QListWidgetItem()
        item.setData(2,str(obj))
        item.setToolTip(replace_variable_value(obj, self.tooltip))
        item.setData(6,obj)
        obj.ui_obj = item
        self.ui_list.addItem(item)


    def filter(self, dict_fields = None , **fields):
        if dict_fields != None:
            fields = dict_fields

        returned_item = []
        fields_keys     = list(fields.keys())
        for item in self.objects:
            fields_values   = list(fields.values())
            item_values     = []

            for key in range(len(fields_keys)):
                var_name = fields_keys[key]

                if var_name[-4:] == '__in':
                    if vars(item)[var_name[:-4]] in fields[var_name] : 
                        fields_values[key] = vars(item)[var_name[:-4]]

                    item_values.append(vars(item)[var_name[:-4]])

                else:
                    item_values.append(vars(item)[var_name])

            if item_values == list(fields_values):
                returned_item.append(item)

        return returned_item


    def get(self, **fields):
        returned_items = self.filter(dict_fields =fields)
        if len(returned_items) >0:
            returned_items = returned_items[0]
        else:
            returned_items = None

        return returned_items

    def temporary_item(self):
        data = {}
        for bit in self.fields:
            data[bit] = self.fields[bit]

        return Item(data, self)



    def create(self,dict_inner_data = None,  **inner_data):
        if dict_inner_data != None:
            inner_data = dict_inner_data

        t_item = self.temporary_item()
        for bit in inner_data:
            setattr(t_item, bit, inner_data[bit])

        if self.before_add == None or self.before_add(t_item):
            
            fields  = []
            data    = []
            for field in inner_data.keys():
                fields.append(str(field))
                if self.fields[field].TYPE in [ [list, dict, set] ,]:
                    inner_data[field] = json.dumps(inner_data[field])
                inner_data[field] = str(inner_data[field])
                data.append(str(inner_data[field]))

            for not_set_field in set(self.fields.keys()).difference(set(inner_data.keys())):
                field_obj = self.fields[not_set_field]
                data.append(str(field_obj.default))


            fields_str = ', '.join(list(fields) + list(set(self.fields.keys()).difference(set(inner_data.keys()))))
            data_str = ', '.join(data)
            

            db_connection = sql.connect(self.INSApp.database_path)

            data_str_f = ', '.join((['?',]* len(data)))

            item = db_connection.execute(f"""INSERT INTO {self.DBTableName} ({fields_str}) values ({data_str_f}) """, data )
            
            db_connection.commit()
            db_connection.close()



            data_n = { fields[i]:data[i] for i in range(len(data)) }
            data_n['view_name'] = self.view_name
            data_n['id'] = int(item.lastrowid)
            data_n['Model'] = self
            item_object = Item(data_n, self)
            self.objects.append(item_object)
            self.add_item_to_list(item_object)


            return item_object
        else:
            False
            

        
    def delete_selected(self):
        item = self.ui_list.currentItem()
        
        if item != None:
            item.data(6).delete()









        
                

class HoverableCurveItem(pg.PlotCurveItem):
    sigCurveHovered = QtCoregraph.Signal(object, object)
    sigCurveNotHovered = QtCoregraph.Signal(object, object)

    def __init__(self, hoverable=True, *args, **kwargs):
        super(HoverableCurveItem, self).__init__(*args, **kwargs)
        self.hoverable = hoverable
        self.setAcceptHoverEvents(True)

    def hoverEvent(self, ev):
        if self.hoverable:
            if self.mouseShape().contains(ev.pos()):
                self.sigCurveHovered.emit(self, ev)
            else:
                self.sigCurveNotHovered.emit(self, ev)