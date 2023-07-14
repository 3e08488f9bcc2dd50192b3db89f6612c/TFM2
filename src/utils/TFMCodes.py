class TFMCodes:
    class game:
        class recv:
            Correct_Version = (28, 1)
            
            
            Set_Language = (176, 1)
            Language_List = (176, 2)
        
        class send:
            Banner_Login = [16, 9]
        
        
            Correct_Version = [26, 3]
            
            
            Image_Login = [100, 99]
            
            Set_Language = [176, 5]
            Language_List = [176, 6]
            Verify_Code = [176, 7]