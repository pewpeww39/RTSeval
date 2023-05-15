format long;
file = readtable("rtsData_Loop1.csv");
column = file(file.Column == 54, :);
data = column(column.Row == 3, :);

signal=data.Vs;
time=data.Ticks;
WL = data.W_L(1);
typeT = data.Type(1);

%                 signal = table2array(T(200:height(T),"DrainI")); %1150:10000 Id DrainI 200
%                 time = table2array(T(200:height(T),"Time")); %1150:10000 Time 200
signal_length = length(signal); 
signal = signal.';
VG=1.2;
signal=VG-signal;
                % fix signal
        % ============================================================================================================================
time =  time.';
len_time = length(time); 
time =  time.';
ft_size=12;
t_round = round(mean(diff(time)*100000))./100000;
Fs = 1/t_round;
Lc = len_time; 

Yd = fft(signal-mean(signal));
P2d = Yd(1:floor(Lc/2)+1);
P1d = abs(P2d).^2/(Fs*Lc);        
P1d(2:end-1) = 2*P1d(2:end-1);
frq = Fs*(0:(Lc/2))/Lc;
%          width=floor(length(signal)/3);
%          [myPSD,frq]=pwelch(signal,hanning(width),floor(width/3),width,Fs);

subplot(3,2,1);

plot(frq(5:end),P1d(5:end)) %P1d myPSD
set(gca, 'YScale', 'log');
set(gca, 'XScale', 'log');
set(gca, 'FontSize', 12);
title(strcat('1/f Signature '),'FontSize', ft_size);
xlabel('frequency (Hz)','FontSize', ft_size);
ylabel('S_I_d (A^2/Hz)','FontSize', ft_size);

%ylim([1*10^-24,1*10^-14]);
% title("1/f Signature")
%set(gca,'FontSize',18)
% tiledlayout(2,3);
% nexttile
ID_LABEL = ("V_{gs} (V)"); 
subplot(3,2,2);
test = histogram(signal,80);
set(gca, 'YScale', 'linear');
set(gca, 'XScale', 'linear');


set(gca, 'FontSize', ft_size);
title(strcat('Histogram '),'FontSize', ft_size);
xlabel(ID_LABEL, 'FontSize', ft_size);
ylabel('Frequency', 'FontSize', ft_size);

% title2 = strcat(file_ptr, ' Time Plot');
% f2 = figure('Name',title2);
%nexttile
subplot(3,2,[3 4]);
plot(time,signal)
set(gca, 'FontSize', ft_size);
title(strcat('Signal Plot '),'FontSize', 10);
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
D = test.Data; 
disp(test.BinWidth);
% figure
% bar(E(:,1:length(E)-1),V, test.BinWidth)
% hold on 
% plot(E(:,1:(length(E)-1)),V)

subplot(3,2,2);
hold on;
yi = smooth(V); 
yi = smooth(yi); 
%  figure
plot(E(:,1:(length(E)-1)),yi,'-k','LineWidth',3)
[pks2,locs] = findpeaks(yi,E(:,1:(length(E)-1)));
% subplot(3,2,2);
% test = histogram(yi,80);
set(gca, 'YScale', 'linear');
set(gca, 'XScale', 'linear');


set(gca, 'FontSize', ft_size);
title(strcat('Amplitude '),'FontSize', ft_size);
xlabel(ID_LABEL, 'FontSize', ft_size);
ylabel('Frequency', 'FontSize', ft_size);


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
% % %     Number_Of_Bin = 30;  
% % %     Number_Of_Bin1 =  30; 
% % %     sum_delta = zeros(1,signal_length-1);
% % %     for i = 1:signal_length-1
% % %         sum_delta(1,i) = time(i+1,1) - time(i,1); 
% % %     end
% % %     Delta_T = mean(sum_delta); 
% % %     myState=zeros(nrows,1);
% % %     L_Level_0 = min(signal(1:signal_length,1));
% % % %             H_Level_0 = min(pks) + delta/2;
% % % %             L_Level_1 = max(pks) - delta/2 + delta/100 ; 
% % %    % H_Level_0 = max(pks(max1),pks(max2)) - delta/2 - delta/100;
% % %     %L_Level_1 = max(pks(max1),pks(max2)) - delta/2 + delta/100 ;
% % % 
% % %     if (length(center) == 2)
% % %         H_Level_0 = min(pks) + delta/2;
% % %         %H_Level_0 = max(pks) - delta/2 - delta/100;
% % %         L_Level_1 = max(pks) - delta/2 + delta/100 ;
% % %     else
% % %         H_Level_0 = max(pks(max1),pks(max2)) - delta/2  - delta/100;
% % %         %H_Level_0 = max(pks(max1),pks(max2)) - delta/2 - delta/100;
% % %         L_Level_1 = max(pks(max1),pks(max2)) - delta/2 + delta/100 ; 
% % %     end
% % %     H_Level_1 = max(signal(1:signal_length,1));
% % % 
% % % 
% % %     for r=1:nrows
% % %         if((signal(r,1)>=(L_Level_0))&&(signal(r,1)<=(H_Level_0)))
% % %             myState(r,1)=0;
% % %         elseif((signal(r,1)>=L_Level_1)&&(signal(r,1)<=(H_Level_1)))
% % %                myState(r,1)=1;
% % %         else
% % %             myState(r,1)=2;
% % % 
% % %         end
% % %     end
    % T0 = Te 
    % T1 = Tc
    
    [w,initcross,finalcross]=pulsewidth(signal,time,'StateLevels',[gaussian_low_level_accoc_current,gaussian_high_level_accoc_current]);
    Tau_0=w;
    finalcross=[0;finalcross(1:length(finalcross)-1)];
    Tau_1=initcross-finalcross;
    subplot(3,2,5);
    histogram(Tau_0,50);
    t0 = smooth(Tau_0); 
    t1= smooth(Tau_1); 
    hold on;
%     plot(t0,'-k','LineWidth',3)
    set(gca, 'YScale', 'linear');
    set(gca, 'XScale', 'linear');
    set(gca, 'FontSize', ft_size);
    title(strcat('Histogram '),'FontSize', ft_size);
    xlabel('Tau12 (s)', 'FontSize', ft_size);
    ylabel('Frequency', 'FontSize', ft_size);
    pos = get(gca, 'Position');
    pos(2) = pos(2) - 0.01; % adjust the y-position of the subplot to make room for the super-title
    set(gca, 'Position', pos);
%     [Tau_0,N_transition_0,f_0]=getTaw(nrows,Delta_T,myState,0,Number_Of_Bin, "test");
    subplot(3,2,6);
    histogram(Tau_1,50);
    set(gca, 'YScale', 'linear');
    set(gca, 'XScale', 'linear');
    set(gca, 'FontSize', ft_size);
    title(strcat('Histogram '),'FontSize', ft_size);
    xlabel('Tau21 (s)', 'FontSize', ft_size);
    ylabel('Frequency', 'FontSize', ft_size);
%     [Tau_1,N_transition_1, f_1]=getTaw(nrows,Delta_T,myState,1,Number_Of_Bin1, "test");
    pos = get(gca, 'Position');
    pos(2) = pos(2) - 0.01; % adjust the y-position of the subplot to make room for the super-title
    set(gca, 'Position', pos);
    %fprintf("Tc = %f \nTe = %f\n",Tau_1,Tau_0)
%     total_transistions = N_transition_0 + N_transition_1;
    total_transistions=length(w);
end
mainT = strcat("RTS Data: ", WL, " ", typeT);
disp(mainT)
sgtitle(mainT, 'interpreter', 'none')