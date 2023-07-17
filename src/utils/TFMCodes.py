class TFMCodes:
    class game:
        class recv:
            
            
            Create_Account = (26, 7)
            Login_Account = (26, 8)
            Get_Captcha = (26, 20)
            Dummy = (26, 26)
            
            
            Correct_Version = (28, 1)
            Computer_Information = (28, 17)
            
            
            Get_Language = (176, 1)
            Language_List = (176, 2)
        
        class send:
            Server_Message = [6, 20]
        
            Banner_Login = [16, 9]
        
        
            Correct_Version = [26, 3]
            Login_Result = [26, 12]
            Set_Captcha = [26, 20]
            
            Queue_popup = [28, 61]

            Image_Login = [100, 99]
            
            Set_Language = [176, 5]
            Language_List = [176, 6]
            Verify_Code = [176, 7]