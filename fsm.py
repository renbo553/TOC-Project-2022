from transitions.extensions import GraphMachine

from utils import send_text_message, push_text_message

from datetime import datetime

# const
NAME_SIZE = 10
DB_TABLE = "Transaction_Record"

MENU_MSG = "主選單命令：\n新增\n刪除\n修改\n查詢"
NO_RESULT_MSG = "該日無任何紀錄"
INPUT_DATE_MSG = "請輸入日期(YYYY-MM-DD)"
INPUT_TYPE_MSG = "請輸入紀錄種類(收入/支出)"
INPUT_NAME_MSG = "請輸入項目名稱(10字以內)"
INPUT_AMOUNT_MSG = "請輸入金額"


class TocMachine(GraphMachine):
    def __init__(self, db, **machine_configs):
        self.db = db
        self.machine = GraphMachine(model=self, **machine_configs)
        self.date_buf = ""
        self.type_buf = ""
        self.name_buf = ""
        self.amount_buf = 0
        self.result_buf = []
        self.index = 0
        self.sum = 0
        self.going_back = False

    def is_going_to_menu(self, event):
        return True

    def is_going_to_insert_0(self, event):
        text = event.message.text
        return text == "新增"

    def is_going_to_insert_1(self, event):
        text = event.message.text
        return self.is_date(text)

    def is_going_to_insert_2(self, event):
        text = event.message.text
        return self.is_type(text)

    def is_going_to_insert_3(self, event):
        text = event.message.text
        if len(text) > NAME_SIZE:
            return False
        return True

    def is_going_to_insert_fin(self, event):
        text = event.message.text
        return text.isdigit()

    def is_going_to_delete_0(self, event):
        text = event.message.text
        return text == "刪除"

    def is_going_to_delete_1(self, event):
        text = event.message.text
        return self.is_date(text)
    
    def is_going_to_delete_fin(self, event):
        text = event.message.text
        if not text.isdigit():
            return False
        return self.is_valid_index(text)

    def is_going_to_modify_0(self, event):
        text = event.message.text
        return text == "修改"

    def is_going_to_modify_1(self, event):
        text = event.message.text
        return self.is_date(text)
        
    def is_going_to_modify_2(self, event):
        text = event.message.text
        if not text.isdigit():
            return False
        return self.is_valid_index(text)

    def is_going_to_modify_3(self, event):
        text = event.message.text
        return self.is_date(text)

    def is_going_to_modify_4(self, event):
        text = event.message.text
        return self.is_type(text)

    def is_going_to_modify_5(self, event):
        text = event.message.text
        if len(text) > NAME_SIZE:
            return False
        return True

    def is_going_to_modify_fin(self, event):
        text = event.message.text
        return text.isdigit()

    def is_going_to_search_0(self, event):
        text = event.message.text
        return text == "查詢"

    def is_going_to_search_fin(self, event):
        text = event.message.text
        return self.is_date(text)
    
    #def on_enter_initial(self, event):
        #print("I'm entering initial")

        #reply_token = event.reply_token
        #send_text_message(reply_token, "Trigger initial")

    def on_exit_initial(self, event):
        print("Leaving initial")

    def on_enter_menu(self, event):
        print("I'm entering menu")

        self.going_back = False

        user_id = event.source.user_id
        global MENU_MSG
        push_text_message(user_id, MENU_MSG)

    def on_exit_menu(self, event):
        print("Leaving menu")

    def on_enter_insert_0(self, event):
        print("I'm entering insert 0")

        reply_token = event.reply_token
        global INPUT_DATE_MSG
        send_text_message(reply_token, INPUT_DATE_MSG)

    def on_exit_insert_0(self, event):
        print("Leaving insert 0")

        text = event.message.text
        self.date_buf = text

    def on_enter_insert_1(self, event):
        print("I'm entering insert 1")

        reply_token = event.reply_token
        global INPUT_TYPE_MSG
        send_text_message(reply_token, INPUT_TYPE_MSG)

    def on_exit_insert_1(self, event):
        print("Leaving insert 1")

        text = event.message.text
        self.type_buf = text
    
    def on_enter_insert_2(self, event):
        print("I'm entering insert 2")

        reply_token = event.reply_token
        global INPUT_NAME_MSG
        send_text_message(reply_token, INPUT_NAME_MSG)

    def on_exit_insert_2(self, event):
        print("Leaving insert 2")

        text = event.message.text
        self.name_buf = text

    def on_enter_insert_3(self, event):
        print("I'm entering insert 3")

        reply_token = event.reply_token
        global INPUT_AMOUNT_MSG
        send_text_message(reply_token, INPUT_AMOUNT_MSG)

    def on_exit_insert_3(self, event):
        print("Leaving insert 3")

        text = event.message.text
        self.amount_buf = int(text)

    def on_enter_insert_fin(self, event):
        print("I'm entering insert fin")

        # insert record into database
        global DB_TABLE
        self.uid_buf = event.source.user_id
        sql = f"INSERT INTO {DB_TABLE} (date, type, name, amount, uid)\
        VALUES ('{self.date_buf}', '{self.type_buf}', '{self.name_buf}', {self.amount_buf}, '{self.uid_buf}')"
        self.db.engine.execute(sql)

        reply_token = event.reply_token
        send_text_message(reply_token, "新增成功")

        self.advance(event)

    def on_exit_insert_fin(self, event):
        print("Leaving insert fin")


    # delete
    def on_enter_delete_0(self, event):
        print("I'm entering delete 0")

        reply_token = event.reply_token
        global INPUT_DATE_MSG
        send_text_message(reply_token, INPUT_DATE_MSG)

    def on_exit_delete_0(self, event):
        print("Leaving delete 0")

        text = event.message.text
        self.date_buf = text

    def on_enter_delete_1(self, event):
        print("I'm entering delete 1")

        reply_token = event.reply_token
        self.fetch_result(event)
        if len(self.result_buf) != 0:
            text = self.create_result_string()
            text += "請輸入欲刪除的紀錄編號"
            send_text_message(reply_token, text)
        else:
            global NO_RESULT_MSG
            send_text_message(reply_token, NO_RESULT_MSG)
            
            self.going_back = True
            self.go_back(event)

    def on_exit_delete_1(self, event):
        print("Leaving delete 1")

        if self.going_back:
            return
        text = event.message.text
        self.index = int(text)

    def on_enter_delete_fin(self, event):
        print("I'm entering delete fin")

        # delete record from database
        id_buf, self.date_buf, self.type_buf, self.name_buf, self.amount_buf, self.uid_buf = self.result_buf[self.index - 1]
        self.result_buf = []
        global DB_TABLE
        sql = f"DELETE FROM {DB_TABLE} WHERE id = {id_buf} AND uid = '{self.uid_buf}'"
        self.db.engine.execute(sql)

        reply_token = event.reply_token
        send_text_message(reply_token, "刪除成功")
        
        self.advance(event)

    def on_exit_delete_fin(self, event):
        print("Leaving delete fin")


    # modify
    def on_enter_modify_0(self, event):
        print("I'm entering modify 0")

        reply_token = event.reply_token
        global INPUT_DATE_MSG
        send_text_message(reply_token, INPUT_DATE_MSG)

    def on_exit_modify_0(self, event):
        print("Leaving modify 0")

        text = event.message.text
        self.date_buf = text

    def on_enter_modify_1(self, event):
        print("I'm entering modify 1")

        reply_token = event.reply_token
        self.fetch_result(event)
        if len(self.result_buf) != 0:
            text = self.create_result_string()
            text += "請輸入欲修改的紀錄編號"
            send_text_message(reply_token, text)
        else:
            global NO_RESULT_MSG
            send_text_message(reply_token, NO_RESULT_MSG)

            self.going_back = True
            self.go_back(event)

    def on_exit_modify_1(self, event):
        print("Leaving modify 1")

        if self.going_back:
            return
        text = event.message.text
        self.index = int(text)

    def on_enter_modify_2(self, event):
        print("I'm entering modify 2")

        reply_token = event.reply_token
        global INPUT_DATE_MSG
        send_text_message(reply_token, INPUT_DATE_MSG)

    def on_exit_modify_2(self, event):
        print("Leaving modify 2")

        text = event.message.text
        self.date_buf = text

    def on_enter_modify_3(self, event):
        print("I'm entering modify 3")

        reply_token = event.reply_token
        global INPUT_TYPE_MSG
        send_text_message(reply_token, INPUT_TYPE_MSG)

    def on_exit_modify_3(self, event):
        print("Leaving modify 3")

        text = event.message.text
        self.type_buf = text

    def on_enter_modify_4(self, event):
        print("I'm entering modify 4")

        reply_token = event.reply_token
        global INPUT_NAME_MSG
        send_text_message(reply_token, INPUT_NAME_MSG)

    def on_exit_modify_4(self, event):
        print("Leaving modify 4")

        text = event.message.text
        self.name_buf = text

    def on_enter_modify_5(self, event):
        print("I'm entering modify 5")

        reply_token = event.reply_token
        global INPUT_AMOUNT_MSG
        send_text_message(reply_token, INPUT_AMOUNT_MSG)

    def on_exit_modify_5(self, event):
        print("Leaving modify 5")

        text = event.message.text
        self.amount_buf = int(text)

    def on_enter_modify_fin(self, event):
        print("I'm entering modify fin")

        # update record from database
        id_bf, date_bf, type_bf, name_bf, amount_bf, uid_bf = self.result_buf[self.index - 1]
        self.result_buf = []
        global DB_TABLE
        sql = f"UPDATE {DB_TABLE} SET date = '{self.date_buf}', type = '{self.type_buf}', name = '{self.name_buf}', amount = {self.amount_buf} WHERE id = {id_bf}"
        print(sql)
        self.db.engine.execute(sql)

        reply_token = event.reply_token
        send_text_message(reply_token, "修改成功")

        self.advance(event)

    def on_exit_modify_fin(self, event):
        print("Leaving modify fin")
    

    # search
    def on_enter_search_0(self, event):
        print("I'm entering search 0")

        reply_token = event.reply_token
        global INPUT_DATE_MSG
        send_text_message(reply_token, INPUT_DATE_MSG)

    def on_exit_search_0(self, event):
        print("Leaving search 0")

        text = event.message.text
        self.date_buf = text

    def on_enter_search_fin(self, event):
        print("I'm entering search fin")

        reply_token = event.reply_token
        self.fetch_result(event)
        text = self.create_result_string()
        text += f"總計  {self.sum}  元"
        send_text_message(reply_token, text)

        self.advance(event)

    def on_exit_search_fin(self, event):
        print("Leaving search fin")


    # utility
    def is_date(self, text):
        try:
            datetime.strptime(text, '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def is_type(self, text):
        if text == "收入" or text == "支出":
            return True
        return False
    
    def is_valid_index(self, text):
        number = int(text)
        number -= 1
        if number >= 0 and number < len(self.result_buf):
            return True
        return False

    def fetch_result(self, event):
        global DB_TABLE
        self.uid_buf = event.source.user_id
        sql = f"SELECT * FROM {DB_TABLE} WHERE uid = '{self.uid_buf}' AND date = '{self.date_buf}'"
        result = self.db.engine.execute(sql)
        self.result_buf = []
        for row in result:
            self.result_buf.append(row)

    def create_result_string(self):
        self.sum = 0
        text = f"該日紀錄({self.date_buf})"
        text += f"\n   金額   名稱"
        for i in range(0, len(self.result_buf)):
            id_bf, date_bf, type_bf, name_bf, amount_bf, uid_bf = self.result_buf[i]
            if type_bf == "支出":
                amount_bf *= -1
            self.sum += amount_bf
            text += f"\n{(i + 1):{2}} {str(amount_bf).ljust(5)} {name_bf}"
        text += "\n"
        return text