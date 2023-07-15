class TFMCodes:
    class game:
        class recv:
            Get_Captcha = (26, 20)
            
            #
            Create_Account = (26, 7)
            
            #
            Correct_Version = (28, 1)
            Computer_Information = (28, 17)
            
            
            # 
            Get_Language = (176, 1)
            Language_List = (176, 2)
        
        class send:
            Server_Message = [6, 20]
        
            Banner_Login = [16, 9]
        
        
            Correct_Version = [26, 3]
            Set_Captcha = [26, 20]
            

            Image_Login = [100, 99]
            
            Set_Language = [176, 5]
            Language_List = [176, 6]
            Verify_Code = [176, 7]