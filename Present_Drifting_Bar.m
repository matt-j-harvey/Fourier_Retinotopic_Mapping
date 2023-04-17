sca 

displayInfo = initialisePsychToolbox;
presentationData = [];
presentationData.sphericalCorrection = 1;
presentationData.oneDirection = 1;
presentationData.trialsPerDirection = 10;
presentationData.sweeps = 10;
presentationData.period = 10;
presentationData.stimWidth = 20;
presentationData.displayInfo = displayInfo;         
presentationData.FPS = 30;
presentationData.squareSize = 25;
presentationData.squareFlipT = 0.166;


Screen('FillRect', displayInfo.winPrimary, displayInfo.white, displayInfo.photodiodeSquare)
flipT = Screen('Flip', displayInfo.winPrimary);

% Maximum priority level
topPriorityLevel = MaxPriority(displayInfo.winPrimary);
Priority(topPriorityLevel);

stimCore = retinotopicMapping(presentationData, nan, flipT);

answer = questdlg('Start retinotopic mapping?');
% Handle response
if ~strcmpi(answer, 'Yes')
    disp('Cancelling')
    return
end

disp('Beginning stimulus presentation')

trialNum = 0;
for stimNum = 1:length(stimCore.trialOrder)
% Log trial data
trialNum = trialNum +1;
fprintf('Presenting trial %d of %d \n', trialNum, length(stimCore.trialOrder)) 
presentationData.trialNumber(trialNum) = trialNum;
presentationData.trialType(trialNum) = stimCore.trialOrder(trialNum);
stimCore.presentNextStimulus;
end

save('C:\Retinotpic_Mapping_Logs\tets_retinotopy.mat', 'presentationData', '-v7.3')
fprintf('Done')
