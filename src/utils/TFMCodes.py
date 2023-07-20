class TFMCodes:
    class tribulle:
        class recv:
            ST_ChangerDeGenre = 10
            ST_AjoutAmi = 18
            ST_RetireAmi = 20
            ST_DemandeEnMariage = 22
            ST_RepondDemandeEnMariage = 24
            ST_DemandeDivorce = 26
            ST_ListeAmis = 28
            ST_FermerListeAmis = 30
            ST_AjoutListeNoire = 42
            ST_RetireListeNoire = 44
            ST_ListeNoire = 46
            ST_EnvoitMessageCanal = 48
            ST_EnvoitTribuMessageCanal = 50
            ST_EnvoitMessagePrive = 52
            ST_RejoindreCanal = 54
            ST_QuitterCanal = 56
            ST_DemandeMembresCanal = 58
            ST_DefinitModeSilence = 60
            ST_InviterMembre = 78
            ST_RepondInvitationTribu = 80
            ST_QuitterTribu = 82
            ST_CreerTribu = 84
            ST_ChangerMessageJour = 98
            ST_ChangerCodeMaisonTFM = 102
            ST_ExclureMembre = 104
            ST_DemandeInformationsTribu = 108
            ST_FermerTribu = 110
            ST_AffecterRang = 112
            ST_RenommerRang = 116
            ST_SupprimerDroitRang = 114
            ST_AjouterRang = 118
            ST_SupprimerRang = 120
            ST_InverserOrdreRangs = 122
            ST_DesignerChefSpirituel = 126
            ST_DissoudreTribu = 128
            ST_ListeHistoriqueTribu = 132
            
        class send:
            ET_ResultatAjoutAmi = 19
            ET_ResultatRetireAmi = 21
            ET_ErreurDemandeEnMariage = 23
            ET_ResultatRepondDemandeEnMariage = 25
            ET_ResultatFermerListeAmis = 31
            ET_SignaleConnexionAmi = 32
            ET_SignaleDeconnexionAmi = 33
            ET_SignaleRetraitAmiBidirectionnel = 35
            ET_SignaleAjoutAmiBidirectionnel = 35
            ET_SignaleAjoutAmi = 36
            ET_SignaleRetraitAmi = 37
            ET_SignaleDemandeEnMariage = 38
            ET_SignaleMariage = 39
            ET_ResultatDemandeEnMariage = 40
            ET_SignaleDivorce = 41
            ET_ResultatAjoutListeNoire = 43
            ET_ResultatRetireListeNoire = 45
            ET_ResultatListeNoire = 47
            ET_ResultatMessageCanal = 49
            ET_RecoitMessagePriveSysteme = 53
            ET_ResultatRejoindreCanal = 55
            ET_ResultatQuitterCanal = 57
            ET_ResultatDemandeMembresCanal = 59
            ET_ResultatDefinitModeSilence = 61
            ET_SignaleRejointCanal = 62
            ET_SignaleQuitteCanal = 63
            ET_SignaleMessageCanal = 64
            ET_SignaleEnvoitTribuMessageCanal = 65
            ET_RecoitMessagePrive = 66
            ET_ResultatInvitationTribu = 79
            ET_ResultatInviterMembre = 81
            ET_ResultatQuitterTribu = 83
            ET_ResultatCreerTribu = 85
            ET_SignaleInvitationTribu = 86
            ET_SignaleNouveauMembre = 89
            ET_SignaleCreerTribu = 89
            ET_SignaleExclusion = 93
            ET_ErreurChangerMessageJour = 99
            ET_ResultatExclureMembre = 105
            ET_ErreurInformationsTribu = 109
            ET_SignaleFermerTribu = 111
            ET_SignaleChangementRang = 113
            ET_ResultatChangerMessageJour = 125
            ET_ResultatDissoudreTribuJour = 127
            ET_ResultatDesignerChefSpirituel = 127
            ET_ResultatDissoudreTribu = 129
            ET_ResultatInformationsTribu = 130
            ET_SignaleConnexionMembre = 131
            ET_ResultatListeHistoriqueTribu = 133
    
    class game:
        class recv:
            Create_Account = (26, 7)
            Login_Account = (26, 8)
            New_Survey = (26, 16)
            Survey_Answer = (26, 17)
            Survey_Result = (26, 18)
            Get_Captcha = (26, 20)
            Dummy = (26, 26)
            Request_Info = (26, 40)
            
            
            Correct_Version = (28, 1)
            Game_Log = (28, 4)
            Computer_Information = (28, 17)
            
            
            # Cafe Packets
            Reload_Cafe = (30, 40)
            Open_Cafe_Topic = (30, 41)
            Create_New_Cafe_Post = (30, 43)
            Create_New_Cafe_Topic = (30, 44)
            Open_Cafe = (30, 45)
            Vote_Cafe_Post = (30, 46)
            Delete_Cafe_Message = (30, 47)
            Delete_All_Cafe_Message = (30, 48)
            
            Tribulle = (60, 3)
            
            Report_Cafe_Post = (149, 4)
            Get_Cafe_Warnings = (149, 5)
            Check_Cafe_Topic = (149, 6)
            
            View_Cafe_Posts = (149, 15)
            
            Get_Language = (176, 1)
            Language_List = (176, 2)
        
        class send:
            Server_Message = [6, 20]
        
            Banner_Login = [16, 9]
        
        
            Player_Identification = [26, 2]
            Correct_Version = [26, 3]
            Login_Result = [26, 12]
            Survey = [26, 16]
            Survey_Answer = [26, 17]
            Set_Captcha = [26, 20]
            Login_Souris = [26, 33]
            
            Time_Stamp = [28, 2]
            Message_Langue = [28, 5]
            Request_Info = [28, 50]
            
            Cafe_Topics_List = [30, 40]
            Open_Cafe_Topic = [30, 41]
            Open_Cafe = [30, 42]
            Cafe_New_Post = [30, 44]
            Delete_Cafe_Message = [30, 47]
            
            Tribulle_Packet = [60, 3]
            Switch_Tribulle = [60, 4]

            Image_Login = [100, 99]
            
            Send_Cafe_Warnings = [144, 11]
            Flash_Player_Attention_Popup = [144, 13]
            Minibox_1 = [144, 17]
            
            Set_Language = [176, 5]
            Language_List = [176, 6]
            Verify_Code = [176, 7]
    
    class old:
        class send:
            Player_Ban_Login = [26, 18]