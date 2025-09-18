clear;
sizeTest;
ImportInputData;
ImportTargetData;
numDados = size(InputData);
%InputData(:,1:2) = InputData(:,1:2) - 273.15;
numTreina = numDados(1)-numTeste; 
%% Selecionando dados de treinamento e teste
inputs = con2seq(InputData(1:numTreina,:)');
targets = con2seq(TargetData(1:numTreina,:)');
%% Treinamento
for n = 1:7
    for i = 1:10 
        net = elmannet(1,n,'trainlm');
        net.divideFcn = 'dividetrain'; 
        %net.divideFcn = 'divideblock';
        net.divideMode = 'time';
        %net.divideParam.trainRatio = 0.7;
        %net.divideParam.valRatio = 0.15;
        %net.divideParam.testRatio = 0.15;
        net.trainParam.show = 5;
        net.trainParam.epochs = 200;
        [net,~] = train(net,inputs,targets);
        %[net,~] = train(net,p,tc);
        nntraintool('close');
        weights(:,i) = getwb(net);

        h = cell2mat(net(con2seq(InputData')))';
        mse(i) = sum((TargetData(numTreina:end,2)-h(numTreina:end,2)).^2)/numTeste;
    end
    [Y,I]=sort(mse);
    ind(n) = Y(1);
    finalWeights(:,n) = {weights(:,I(1))};
    clear weights; 
end
[Y,I]=sort(ind);
final_n = I(1);
net = elmannet(1,final_n,'trainlm');
net.divideFcn = 'dividetrain'; 
net.divideMode = 'time';
net.trainParam.epochs = 10;
[net,~] = train(net,inputs,targets);
nntraintool('close');
net = setwb(net,cell2mat(finalWeights(:,final_n)));
% plotTeste;
% output weights
inputWeights = cell2mat(net.IW(1));
WeightsContexHidden = cell2mat(net.LW(1));
WeightsHiddenToOuput = cell2mat(net.LW(2));
bias1 = cell2mat(net.b(1));
bias2 = cell2mat(net.b(2));

%% salva pesos
[m,~] = size(inputWeights);
WeightsInputWithBias = [inputWeights zeros(m,1)];
WeightsContexHiddenWithBias = [WeightsContexHidden bias1];
WeightsHiddenToOuputWithBias = [WeightsHiddenToOuput bias2];
save WeightsInputWithBias.txt WeightsInputWithBias -ascii
save WeightsContexHiddenWithBias.txt WeightsContexHiddenWithBias -ascii
save WeightsHiddenToOuputWithBias.txt WeightsHiddenToOuputWithBias -ascii
save NNDetails.txt final_n -ascii

exit;