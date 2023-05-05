function [taw,Number_transition, f_exp]=getTaw(nrows, Delta_T, myState, State,Number_of_Bins, f_name)
%%f_name = ''; 
%nrows: length(RTS waveform);
%Delta_T: t3(2,1)-t3(1,1); This is the time takes to record each point in
%the RTS wafeform
%myState: trasnfering RTS data to digital value 0 or 1 
%State: corresponds to level 1 or level 2 int RTS waveform
%Number_of_Bins: this is for Average capture or emission time histogram

Number_of_bin=Number_of_Bins;
Ro=length(myState);%nrows;
T=Delta_T;
%St=myState;
Final=zeros(nrows,1);
myDuration=zeros(nrows,1);
%Num=Num.st;

for R=1:Ro
    
     if(myState(R,1)==State)
        myDuration(R,1)=T;
     else
        myDuration(R,1)=0;
     end
end

%Time_at_Level_0=sum(myDuration_0);

Acumalated_Duration_level=timehist(myDuration)';
% I am passing the state into timehist funcation 
% to find total taw up and down            
%Nume_trans=length(find(Acumalated_Duration_level>0));
                                                     
x=length(Acumalated_Duration_level);
good_Acumalated_Duration_level=sort(Acumalated_Duration_level,'descend'); % to find the vector contians taw up and down 
j=1;                                                                        % without the zeros element
 
for i=1:x
    if(good_Acumalated_Duration_level(i,1)>0)
         Final_good_Acumalated_Duration_level(i,1)=good_Acumalated_Duration_level(i,1);
    end
end

[hh,xout]=hist(Final_good_Acumalated_Duration_level,Number_of_bin); % This is will return total bins were generated and its frequency
numer_0f_bins=xout';  % totla bins
freq_Magnitude=hh';

for i=20:5:200
    [HH,Xout]=hist(Final_good_Acumalated_Duration_level,i); % This is will return total bins were generated and its frequency
    Num_Bin=Xout';  % totla bins
    Freq_Mag=HH';
    for j=1:length(Num_Bin)
    Mul_Taw_With_frequen(j,1)=Num_Bin(j,1)*Freq_Mag(j,1);
    %Taw(i,1)=(sum(Mul_Taw_With_frequen))/(sum(Freq_Mag));
    j=j+1;
    end
    T=[T,(sum(Mul_Taw_With_frequen))/(sum(Freq_Mag))];
    
end

% figure;
% plot((20:5:205),T,'r')
% title(['Average Time Constant Vs. Number of Bin for Level ' int2str(State)])
% xlabel('Number of Bins');
% ylabel('Average Time Constant (S)');
% set(gca,'YMinorGrid','on')
% set(gca,'XMinorGrid','on')

for i=1:length(freq_Magnitude)
    Multib_taw_with_frequen(i,1)=numer_0f_bins(i,1)*freq_Magnitude(i,1);
end
taw=(sum(Multib_taw_with_frequen))/(sum(freq_Magnitude));

%stringState=[num2str(State)];
%gtext({stringState})


%f_exp = figure('Name',f_name);
f_exp = 's'; 
hist(Final_good_Acumalated_Duration_level,Number_of_bin);
%showfit exp;
set(gca, 'FontSize', 22);
title(['Histogram of Level ' int2str(State)],'FontSize', 10);
%title('Histogram of Level')
xlabel('Time (s) ', 'FontSize', 22);
ylabel('Frequency ', 'FontSize', 22);
% type = ''; 
% if State
%     type = 'Taw12'; 
% else
%     type = 'Taw21';
% end
% f_name = strcat(f_name, 'RTN_', type); 
% file_name = sprintf('Figures\\Successful\\%s.png', f_name);
% saveas(f, file_name, 'png');
Number_transition=length(find(Acumalated_Duration_level>0));
end
