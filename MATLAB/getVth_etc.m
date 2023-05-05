function [Vth,On_current, Sub_swing, max_gm, specific_gm]=getVth_etc(specific_Vg, T)
% filename= (Temp+"KIdVgSweepVwellVd100m");
% T = readtable(filename,'HeaderLines',257);
%     4200 machine gate voltage column 4 drain current column1   

%        if machine ==0     
%             Vg = table2array(T(:,2));
%             Ig = smooth(table2array(T(:,3)));
%             Id = (table2array(T(:,4)));
%             Is = smooth(table2array(T(:,5)));
%        else 
%             Vg = table2array(T(:,4)); 
%             Id = (table2array(T(:,1)));
%        end
                headers = T.Properties.VariableNames;
                Vg_Index = find(headers=="GateV" | headers=="Vg");
                Id_Index = find(headers=="DrainI" | headers=="Id");
                Vg = table2array(T(:,Vg_Index));
                Id = (table2array(T(:,Id_Index)));
                Id1=abs(Id);
                gm = smooth(gradient(Id1)./gradient(Vg));
                sqId= sqrt(Id1);
                logId= log10(Id1);
                dsqId = (gradient(sqId)./gradient(Vg));
                dlogId =(gradient(logId)./gradient(Vg));
                [slope , VgIdx ]= max(dsqId);
                
                max_gm=max(gm);
                [deltaVg, gmIdx]= min(abs(Vg-str2double(specific_Vg)));
                specific_gm= gm(gmIdx);
                On_current =max(Id1);
                
                C = (slope*(Vg- Vg(VgIdx))) + sqId(VgIdx);
                Vth = (-sqId(VgIdx)/slope)+Vg(VgIdx);
                [diff, IdxVth]= min(abs(Vg-Vth));
                InvSS =dlogId(IdxVth-10);
                Sub_swing = 1000/InvSS ;
                %figure(3);
                yyaxis left
                hold on
                            
                plot(Vg, sqId);
                
               % subplot(4,2,7) 
               plot(Vg,C);
                ylabel('sqrt(Id)')
                yyaxis right
                plot(Vg, dsqId);
                ylabel('Delta sqrt(Id)')
                %subplot(4,2,8) 
                 
                 xlabel('Vg (V)');
                 title(strcat("Id vs. Vg at Vth = ",num2str(Vth)));
                 hold off
