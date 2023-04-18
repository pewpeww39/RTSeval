close all 
clear
file_loc_dir = 'C:\SkyWater\Packaged_Parts\4209926_W22_Dev7CC9T08AC_RTS_Modeling_300K\Wafer_22';
test_folder_dir = dir(file_loc_dir);    
name_dirs = {length(test_folder_dir)-5};

%loop begins at 6 call it main_dir_count
for main_dir_count = 3:length(test_folder_dir)
store_dir = test_folder_dir(main_dir_count).name;
file_ptr_dir= convertCharsToStrings(store_dir);
file_loc_close = strcat(file_loc_dir,'\', file_ptr_dir);
test_folder_close = dir(file_loc_close);    
name_close = {length(test_folder_close)-2};
    %next loop begins at 3 call it sub_dir_count
    for sub_dir_count = 3:length(test_folder_close)
    store_close = test_folder_close(sub_dir_count).name;
    file_ptr_close= convertCharsToStrings(store_close);
    file_loc = strcat(file_loc_close,'\', file_ptr_close);

        test_folder = dir(file_loc);
        name = {length(test_folder)-5};
        table_store = table;
        table_store2 = table;
        table_store3 = table;
        cell_store = cell(numel(test_folder),1);
        for w = 6:length(test_folder)
             % W offset is: 5, 2 for . .. and 3 for: 'Id-Vg_Vd', 'Id-Vg_Vd', 'IdVd'
             store = test_folder(w).name; 
             id_vg = test_folder(3).name; 
             id_vg = convertCharsToStrings(id_vg); 
             id_vg = strcat(file_loc,'\', id_vg);
             file_ptr= convertCharsToStrings(store);
             name{w-5} = file_ptr; 
             %Z = readtable(file_ptr,'HeaderLines',255);
             file_ptr = strcat(file_loc,'\', file_ptr); 
             T = readtable(file_ptr,'HeaderLines',0); %255 0 
             Id_vg_table = readtable(id_vg,'HeaderLines',0); %256 0
               
             if (height(T)==height(T))
                %Q = readtable(name{1},'HeaderLines',255);
                signal = table2array(T(200:height(T),"DrainI")); %1150:10000 Id DrainI 200
                time = table2array(T(200:height(T),"Time")); %1150:10000 Time 200
                signal_length = length(signal); 
                
                signal = signal.'; 
                
                % fix signal
        % ============================================================================================================================
                time =  time.';
                len_time = length(time); 
        %         divisor = time(len_time); 
        %         points_per_sec = len_time / divisor; 
        %         ten_sec = points_per_sec * 10; 
        %         ten_sec = round(ten_sec); 
        %         start_index = len_time - ten_sec; 
        %         
        %         Id_ideal = mean(signal(start_index:len_time)); 
        %         
        %         degree = 10; % 50 10
        %         
        %         p = polyfit(time, signal, degree);
        %         baseline = polyval(p, time);
        %         
        %         straightened_sig = signal - baseline; 
        %         
        % %         straightened_sig = detrend(signal); 
        %         straightened_sig = straightened_sig + Id_ideal; 
        %         signal = straightened_sig; 
                time =  time.';
        %         % end fix signal 
        % ===========================================================================================================================
               
        
               ft_size = 22; 
                names = split(file_loc, {'\', '_', '--','K', 'Module'}); 
                names2 = file_ptr; 
                names2 = erase(names2,file_loc); 
                names2 = erase(names2,'\');
                names2 = split(names2, {'_', 'RTS', 'Vg', 'Vd', '.csv', 'V'}); 
                DOE = "1"; 
                Experiment = "DryOxidation_50%NO"; 
                mod = names(17);
                mod = mod(1); 
                Device_type = ""; 
                n_pMOS = ''; 
                if (strcmp( mod ,'8000'))
                   Device_type = "nMOS_ThinGateLowVt_1.2V"; 
                   n_pMOS = "N"; 
                elseif(strcmp( mod ,"8006"))
                   Device_type = "pMOS_ThinGateLowVt_1.2V"; 
                   n_pMOS = "P";
                elseif(strcmp( mod ,"8060"))
                   Device_type = "nMOS_ThickGateHighVt_3.3V"; 
                   n_pMOS = "N";
                elseif(strcmp( mod ,'8030'))
                   Device_type = "nMOS_ThickGateHighVt_3.3V"; 
                   n_pMOS = "N";
                elseif(strcmp( mod ,'8068'))
                   Device_type = "pMOS_ThickGateHighVt_3.3V"; 
                   n_pMOS = "P";
                elseif(strcmp( mod ,'8038'))
                   Device_type = "pMOS_ThickGateHighVt_3.3V"; 
                   n_pMOS = "P";
                else 
                   Device_type = "nMOS_ThickGateHighVt_3.3V"; 
                   n_pMOS = "N";
                end
                W = names(20); 
                L = names(21); 
                W = erase(W, 'W'); 
                W = erase(W, 'nm');
                L = erase(L, 'L'); 
                L = erase(L, 'nm');
                
                W_L = strcat('0.',W,'/','0.',L); 
                W_L = W_L(1); 
                Vg = names2(3); 
                Vg = Vg(1); 
                Vd = names2(6);
                Vd = Vd(1); 
                if (contains(Vd, 'm'))
                    front = '0.'; 
                    Vd = erase(Vd, 'm');
                    Vd = strcat(front, Vd); 
                elseif(contains(Vg, 'm'))
                    front = '0.'; 
                    Vg = erase(Vg, 'm');
                    Vg = strcat(front, Vg); 
                end
                Id = mean(signal); % T.Id  T.DrainI
                Vth = "";
                gm = "";
                s_s = "";
                temp = names(10);
                dieX = names(14);
                dieX = erase(dieX, 'X'); 
                dieY = names(15);
                dieY = erase(dieY, 'Y'); 
                taw12 = 0;
                taw21 = 0; 
                taw32 = ""; 
                taw23 = ""; 
                RTSAmplitude_A = 0; 
                RTSAmplitude_B = ""; 
                NumofTransition_A = 0; 
                NumofTransition_B = ""; 
                wl_file = strrep(W_L, '/', '-'); 
                 f = figure('Name',file_ptr);
                
                subplot(3,2,6) 
                [Vth,On_current, s_s, max_gm, gm]=getVth_etc(Vg, Id_vg_table);

                fname = strcat(mod, '_', Device_type,  '_',wl_file , '_VG_', Vg, '_VD_', Vd, '_', temp, 'K_X_', dieX, '_Y_', dieY);
        
        
                
               
                fname_figs = strrep(fname, '_', '-'); 
                t_round = round(mean(diff(time)*1000))./1000;
                Fs = 1/t_round;
                Lc = len_time; 
        
                Yd = fft(signal-mean(signal));
                P2d = Yd(1:floor(Lc/2)+1);
                P1d = abs(P2d).^2/(Fs*Lc);        
                P1d(2:end-1) = 2*P1d(2:end-1);
                frq = Fs*(0:(Lc/2))/Lc;
        %          width=floor(length(signal)/3);
        %          [myPSD,frq]=pwelch(signal,hanning(width),floor(width/3),width,Fs);
        
                subplot(3,2,3);
               
                plot(frq(5:end),P1d(5:end)) %P1d myPSD
                set(gca, 'YScale', 'log');
                set(gca, 'XScale', 'log');
                set(gca, 'FontSize', ft_size);
                title(strcat('1/f Signature ',fname_figs),'FontSize', 10);
                xlabel('frequency (Hz)','FontSize', ft_size);
                ylabel('S_I_d (A^2/Hz)','FontSize', ft_size);
                
                %ylim([1*10^-24,1*10^-14]);
               % title("1/f Signature")
                %set(gca,'FontSize',18)
               % tiledlayout(2,3);
               % nexttile
               ID_LABEL = ("I_{ds} (A)"); 
               subplot(4,2,1);
                test = histogram(signal,50);
               set(gca, 'YScale', 'linear');
                set(gca, 'XScale', 'linear');
        
                
                set(gca, 'FontSize', ft_size);
                title(strcat('Histogram ',fname_figs),'FontSize', 10);
                xlabel(ID_LABEL, 'FontSize', ft_size);
                ylabel('Frequency', 'FontSize', ft_size);
                
               % title2 = strcat(file_ptr, ' Time Plot');
               % f2 = figure('Name',title2);
                %nexttile
                subplot(3,2,2);
                plot(time,signal)
                set(gca, 'FontSize', ft_size);
                title(strcat('Signal Plot ',fname_figs),'FontSize', 10);
                ylabel(ID_LABEL, 'FontSize', ft_size); 
                xlabel('Time (S)', 'FontSize', ft_size);
        
                pos = get(gca, 'Position');
                pos(3) = pos(3) + 0.05; % adjust the y-position of the subplot to make room for the super-title
                set(gca, 'Position', pos);

        
        
        %         B = test.BinEdges;
        %         D = test.Data; 
        %         C = histc(D,B);
        %         
        %         prm = polyfit(B, C, 6);
        %         d1prm = polyder(prm);               % First Derivative (D1)
        %         d2prm = polyder(d1prm);             % Second Derivative (D2)
        %         rd1prm = roots(d1prm);              % All Extrema Locations
        %         xtr = polyval(d2prm,rd1prm);        % Evaluate D2 At All Extrema Locations
        %         pks = rd1prm(xtr < 0); % Peaks Are Where D2 < 0
        %         
        %         delta = abs(abs(max(pks)) - abs(min(pks)));
                % disp('\n')
                % disp(file_ptr)
                % disp(pks)
                % disp('\n')
                % figure
                %plot(time, signal) 
        
                V = test.Values;
                E = test.BinEdges;
                %D = test.Data; 
                %disp(test.BinWidth);
                %figure
                %bar(E(:,1:25),V, test.BinWidth)
                %hold on 
               % plot(E(:,1:(length(E)-1)),V)
                
                %figure 
                yi = smooth(V); 
                yi = smooth(yi); 
                %plot(E(:,1:(length(E)-1)),yi)
              %  figure
               % plot(E(:,1:(length(E)-1)),yi)
                [pks2,locs] = findpeaks(yi,E(:,1:(length(E)-1)));
                
                
                %hold off
               % figure 
                [L_1,tst] = islocalmax(V);
                left = E(L_1);
                right = E([false L_1]);
                center = (left + right)/2;
               % plot(center, V(L), 'o')
                pks = center;
                tst = tst(L_1); 
                
                [max_freq,pos_max] = max(pks2);
                max_ID = locs(pos_max); 
                temp_psk2 = pks2; 
                temp_psk2(pos_max) = 0; 
        
                [max_freq2,pos_max2] = max(temp_psk2);
                max_ID2 = locs(pos_max2); 
                
                gaussian_high_level = 0; 
                gaussian_low_level = 0;  
                gaussian_high_level_accoc_current = 0;
                gaussian_low_level_accoc_current = 0;
        
                binEdges_hst = linspace(min(signal), max(signal), 50);
                binCenters = (binEdges_hst(1:end-1) + binEdges_hst(2:end)) / 2;
                counts_hst = histcounts(signal, binEdges_hst);
                
                
        
                if (max_ID2 > max_ID)
                    gaussian_high_level_accoc_current = max_ID2;
                    [~, index_hst] = min(abs(binCenters - gaussian_high_level_accoc_current));
                    gaussian_high_level = counts_hst(index_hst);
                    
                    gaussian_low_level_accoc_current = max_ID; 
                    [~, index_hst] = min(abs(binCenters - gaussian_low_level_accoc_current));
                    gaussian_low_level = counts_hst(index_hst);
                else
                    gaussian_high_level_accoc_current = max_ID;
                    [~, index_hst] = min(abs(binCenters - gaussian_high_level_accoc_current));
                    gaussian_high_level = counts_hst(index_hst);
                    
                    gaussian_low_level_accoc_current = max_ID2; 
                     [~, index_hst] = min(abs(binCenters - gaussian_low_level_accoc_current));
                    gaussian_low_level = counts_hst(index_hst);
        
                end
                if length(locs) <= 1
                    gaussian_low_level = 0;
                    gaussian_low_level_accoc_current = 0; 
                end
        
                signal = signal.'; 
                nrows=length(signal);
                ncols=1;
                
                
                 
                pdf_name = strcat(names(5),'_', names(6), '_',names(7),'_',mod, '_', Device_type, '_', temp, 'K.pdf');
                fname = fname; 
                if (length(locs) > 1)
                    
        
                    if (length(center) == 2)
                    delta = abs(abs(max(pks)) - abs(min(pks)));
                        else
                            counts = V(L_1); 
                            [x,y] = max(counts); 
                            max1 = y; 
                            counts(y) = 0; 
                            [x,y] = max(counts); 
                            max2 = y; 
                            if ( abs((center(max1) - center(max2))/test.BinWidth) > 7 ) 
                                delta = abs(abs(pks(max1)) - abs(pks(max2)));
                            else
                                counts(max2) = 0; 
                                times_run = 0; 
                                while( (abs((center(max1) - center(max2))/test.BinWidth) < 7 ) && times_run<= length(counts))
                                    [x,y] = max(counts); 
                                    max2 = y;
                                    counts(max2) = 0;
                                    times_run = times_run  + 1; 
                                end
                                delta = abs(abs(pks(max1)) - abs(pks(max2)));
                            end
                    end
                    %sampling_rate = length(signal) / (max(time)-min(time));
                   % Delta_T = time(2,1) - time(1,1);  
                    Number_Of_Bin = 30;  
                    Number_Of_Bin1 =  30; 
                    sum_delta = zeros(1,signal_length-1);
                    for i = 1:signal_length-1
                        sum_delta(1,i) = time(i+1,1) - time(i,1); 
                    end
                    Delta_T = mean(sum_delta); 
                    myState=zeros(nrows,1);
                    L_Level_0 = min(signal(1:signal_length,1));
        %             H_Level_0 = min(pks) + delta/2;
        %             L_Level_1 = max(pks) - delta/2 + delta/100 ; 
                   % H_Level_0 = max(pks(max1),pks(max2)) - delta/2 - delta/100;
                    %L_Level_1 = max(pks(max1),pks(max2)) - delta/2 + delta/100 ;
        
                    if (length(center) == 2)
                        H_Level_0 = min(pks) + delta/2;
                        %H_Level_0 = max(pks) - delta/2 - delta/100;
                        L_Level_1 = max(pks) - delta/2 + delta/100 ;
                    else
                        H_Level_0 = max(pks(max1),pks(max2)) - delta/2  - delta/100;
                        %H_Level_0 = max(pks(max1),pks(max2)) - delta/2 - delta/100;
                        L_Level_1 = max(pks(max1),pks(max2)) - delta/2 + delta/100 ; 
                    end
                    H_Level_1 = max(signal(1:signal_length,1));
                    
                    
                    for r=1:nrows
                        if((signal(r,1)>=(L_Level_0))&&(signal(r,1)<=(H_Level_0)))
                            myState(r,1)=0;
                        elseif((signal(r,1)>=L_Level_1)&&(signal(r,1)<=(H_Level_1)))
                               myState(r,1)=1;
                        else
                            myState(r,1)=2;
                       
                        end
                    end
                    % T0 = Te 
                    % T1 = Tc
                    subplot(3,2,4);
                    [Tau_0,N_transition_0,f_0]=getTaw(nrows,Delta_T,myState,0,Number_Of_Bin, fname);
                    subplot(3,2,5);
                    [Tau_1,N_transition_1, f_1]=getTaw(nrows,Delta_T,myState,1,Number_Of_Bin1, fname);
                    
                    %fprintf("Tc = %f \nTe = %f\n",Tau_1,Tau_0)
                    total_transistions = N_transition_0 + N_transition_1;
        
                   % current_id = mean(T.Id); 
                    %names = split(file_ptr, {'_', 'K'}); 
                    %temp = names(3)
                    % vd = names(4)
                    % vg = names(5)
                    NumofTransition_A = total_transistions; 
                    taw12 = Tau_0; 
                    taw21 = Tau_1;
                    RTSAmplitude_A = delta; 
                    file_name = sprintf('Figures\\Successful\\%s.png', fname);
                    saveas(f, file_name, 'png');
                    table_store(w-5,:)= table(delta, Tau_1, Tau_0, fname, total_transistions,'VariableNames', { 'Delta_Id(A)', 'Tc(s)', 'Te(s)', 'File_Name', 'Number_trasnistions'});  
                    f.WindowState = 'maximized';
                    exportgraphics(f, pdf_name,'ContentType','image','Append',true);
        %             f2.WindowState = 'maximized';
        %             exportgraphics(f2, pdf_name,'ContentType','image','Append',true);
        %             f_0.WindowState = 'maximized';
        %             exportgraphics(f_0, pdf_name,'ContentType','image','Append',true);
        %             f_1.WindowState = 'maximized';
        %             exportgraphics(f_1, pdf_name,'ContentType','image','Append',true);
                else 
                    file_name = sprintf('Figures\\Unsuccessful\\%s.png', fname);
                    saveas(f, file_name, 'png');
                    yes = "Yes"; 
                    table_store2(w-5,:)= table(yes,fname,'VariableNames', { 'Failed', 'File_Name'});
                    f.WindowState = 'maximized';
                    exportgraphics(f, pdf_name,'ContentType','image','Append',true);
        %              f2.WindowState = 'maximized';
        %              exportgraphics(f2, pdf_name,'ContentType','image','Append',true);
                end
                
                table_store3(w-5,:)= table(DOE, Experiment, mod, n_pMOS, Device_type, W_L, Vg, Vd, abs(Id), Vth, gm, s_s, temp, dieX, dieY, taw12, taw21, taw32, taw23, RTSAmplitude_A, RTSAmplitude_B, NumofTransition_A, NumofTransition_B,gaussian_high_level,gaussian_high_level_accoc_current,gaussian_low_level, gaussian_low_level_accoc_current, 'VariableNames', { 'DOE', 'Experiment','Mod', 'n/pMOS', 'Device type', 'W/L', 'Vg(V)', 'Vd(V)', 'Id(A)', 'Vth(V)', 'gm(S)', 'SS (mV/decade)','Temp (K)', 'DieX', 'DieY', 'Taw12(s)', 'Taw21(s)', 'Taw32(s)', 'Taw23(s)' , 'RTSAmplitude_A(A)', 'RTSAmplitude_B(A)', '#ofTransition_A', '#ofTransition_B', 'Frequnecy of High Level Current', 'Current Value (High)', 'Frequnecy of Low Level Current', 'Current Value (Low)'} );
               %                                                                                                                                                                                                                                    gaussian_high_level = 0; 
                                                                                                                                                                                                                                                        %gaussian_low_level = 0;  
                                                                                                                                                                                                                                                        %gaussian_high_level_accoc_current = 0;
                                                                                                                                                                                                                                                        %gaussian_low_level_accoc_current = 0;
        
             end
            clearvars -except table_store table_store2 w yes test_folder name file_loc table_store3 file_names file_loc_dir test_folder_dir name_dirs main_dir_count store_dir file_ptr_dir file_loc_close test_folder_close name_close sub_dir_count store_close file_ptr_close
        end
        names = split(file_loc, {'\', '_', '--','K', 'Module'});  
        mod = names(17);
        mod = mod(1); 
        Device_type = ""; 
        n_pMOS = ''; 
        if (strcmp( mod ,'8000'))
           Device_type = "nMOS_ThinGateLowVt_1.2V"; 
           n_pMOS = "N"; 
        elseif(strcmp( mod ,"8006"))
           Device_type = "pMOS_ThinGateLowVt_1.2V"; 
           n_pMOS = "P";
        elseif(strcmp( mod ,"8060"))
           Device_type = "nMOS_ThickGateHighVt_3.3V"; 
           n_pMOS = "N";
        elseif(strcmp( mod ,'8030'))
           Device_type = "nMOS_ThickGateHighVt_3.3V"; 
           n_pMOS = "N";
        elseif(strcmp( mod ,'8068'))
           Device_type = "pMOS_ThickGateHighVt_3.3V"; 
           n_pMOS = "P";
        elseif(strcmp( mod ,'8038'))
           Device_type = "pMOS_ThickGateHighVt_3.3V"; 
           n_pMOS = "P";
        end
        W = names(20); 
        L = names(21); 
        W = erase(W, 'W'); 
        W = erase(W, 'nm');
        L = erase(L, 'L'); 
        L = erase(L, 'nm');
        W_L = strcat('0.',W,'/','0.',L); 
        W_L = W_L(1); 
        temp = names(10);
        dieX = names(14);
        dieX = erase(dieX, 'X'); 
        dieY = names(15);
        dieY = erase(dieY, 'Y'); 
        wl_file = strrep(W_L, '/', '-'); 
        fname = strcat(mod, '_', Device_type,  '_',wl_file , '_', temp, 'K_X_', dieX, '_Y_', dieY); 
        
        writetable(table_store, strcat('Successful\\',fname,'successful_extracts.csv'))
        writetable(table_store2, strcat('Unsuccessful\\',fname,'unsuccessful_extracts.csv'))
        writetable(table_store3, strcat('Summary_RTS\\',fname,'Summary_Of_RTN.csv'))
        close all 
    end
end



file_loc = 'C:\SkyWater\Summary_RTS' ;
test_folder = dir(file_loc);
name = {length(test_folder)-2};
%combined = [{ 'DOE', 'Experiment','Mod', 'n/pMOS', 'Device type', 'W/L', 'Vg(V)', 'Vd(V)', 'Id(A)', 'Vth(V)', 'gm(S)', 'Temp (K)', 'DieX', 'DieY', 'Taw12(s)', 'Taw21(s)', 'Taw32(s)', 'Taw23(s)' , 'RTSAmplitude_A(A)', 'RTSAmplitude_B(A)', '#ofTransition_A', '#ofTransition_B'}]; 
%combined = [ { 'DOE', 'Experiment','Mod', 'n/pMOS', 'Device type', 'W/L', 'Vg(V)', 'Vd(V)', 'Id(A)', 'Vth(V)', 'gm(S)', 'Temp (K)', 'DieX', 'DieY', 'Taw12(s)', 'Taw21(s)', 'Taw32(s)', 'Taw23(s)' , 'RTSAmplitude_A(A)', 'RTSAmplitude_B(A)', '#ofTransition_A', '#ofTransition_B', 'Frequnecy of High Level Current', 'Current Value (High)', 'Frequnecy of Low Level Current', 'Current Value (Low)'}];
combined= [{ 'DOE', 'Experiment','Mod', 'n/pMOS', 'Device type', 'W/L', 'Vg(V)', 'Vd(V)', 'Id(A)', 'Vth(V)', 'gm(S)', 'SS (mV/decade)','Temp (K)', 'DieX', 'DieY', 'Taw12(s)', 'Taw21(s)', 'Taw32(s)', 'Taw23(s)' , 'RTSAmplitude_A(A)', 'RTSAmplitude_B(A)', '#ofTransition_A', '#ofTransition_B', 'Frequnecy of High Level Current', 'Current Value (High)', 'Frequnecy of Low Level Current', 'Current Value (Low)'}];
                  
for w = 3:length(test_folder)
     store = test_folder(w).name; 
     file_ptr= convertCharsToStrings(store);
     newSheet = readcell(file_ptr);
     combined = [combined; newSheet(2:end,:)]; 

end

T = cell2table(combined(2:end,:),'VariableNames',combined(1,:));

writetable(T,'Full_RTN_Params.csv')


