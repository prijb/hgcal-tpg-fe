// Extension to stage2CPCalcSelectedWord.cpp where this processes all the words in the Rx and Tx files along with tabulating the results

#include <iostream>
#include "L1Trigger/DemonstratorTools/interface/utilities.h"
#include "DataFormats/L1THGCal/interface/HGCalCluster_HW.h"

#include "TPGBEDataformat.hh"
#include "Stage2.hh"

#include "TPGStage2Configuration.hh"
#include "TPGClusterProperties.hh"
#include "TPGLSBScales.hh"

int main(int argc, char** argv)
{
  // Input arguments
  std::string inputFileNameRx, inputFileNameTx;
  std::string outputAccumulInputFileName = "compareFwAccumulatorInput.txt";
  std::string outputFileName = "compareFwEmul.txt";
  std::string outputFileNameProp = "compareFwEmulProp.txt";
  size_t offsetRx = 0;

  if (argc == 3){
    inputFileNameRx = argv[1];
    inputFileNameTx = argv[2];
    std::cout << "Input file for Rx: " << inputFileNameRx << std::endl;
    std::cout << "Input file for Tx: " << inputFileNameTx << std::endl;
    std::cout << "No Rx offset provided, default to 0." << std::endl;
  }
  else if (argc == 4) {
    inputFileNameRx = argv[1];
    inputFileNameTx = argv[2];
    offsetRx = std::stoul(argv[3]);
    std::cout << "Input file for Rx: " << inputFileNameRx << std::endl;
    std::cout << "Input file for Tx: " << inputFileNameTx << std::endl;
    std::cout << "Rx offset: " << offsetRx << std::endl;
  } 
  else {
    std::cerr << "Usage: " << argv[0] << " <input_file_rx> <input_file_tx>" << " <offset_rx>" << std::endl;
    return 1;
  }
  std::cout << std::endl;

  // Extract the relevant data from the input file (Rx)
  l1t::demo::BoardData inputsRx = l1t::demo::read(inputFileNameRx, l1t::demo::FileFormat::EMPv2);
  auto nChannelsRx = inputsRx.size();
  auto nFramesRx = inputsRx.begin()->second.size();

  std::cout << "Reading Rx file" << std::endl;
  std::cout << "Board from file: " << inputFileNameRx << std::endl;
  std::cout << "Board data name : " << inputsRx.name() << ", and number of channels are: " << nChannelsRx  << " with number of frames: " << nFramesRx << std::endl;
  std::cout << std::endl;

  // List of accumulator words
  std::vector<std::map<int, uint64_t>> accumulatorFrames;
  size_t i_channel_rx = 0;
  uint64_t frameWord;

  for (size_t i_frame_rx=0; i_frame_rx < nFramesRx; ++i_frame_rx) {
    std::map<int, uint64_t> accumulatorFrame;
    for (const auto& channel_data: inputsRx) {
      if (i_channel_rx > 16) break; // Limit to 17 channels
      auto channel_frames = channel_data.second;
      frameWord = channel_frames[i_frame_rx].data.to_uint64();
      accumulatorFrame.insert(std::pair<int, uint64_t>(i_channel_rx, frameWord));
      i_channel_rx++;
    }
    accumulatorFrames.push_back(accumulatorFrame);
    i_channel_rx = 0; // Reset for the next frame
  }
  std::cout << "Accumulator frames filled from Rx data." << std::endl;
  std::cout << std::endl;

  /*
  // Print out the accumulator frames
  for (size_t i_frame = 0; i_frame < accumulatorFrames.size(); ++i_frame) {
    std::cout << "Frame " << i_frame << ": ";
    for (const auto& word : accumulatorFrames[i_frame]) {
      std::cout << std::hex << std::setw(16) << std::setfill('0') << word.second << " ";
    }
    std::cout << std::dec << std::endl;
  }
  */

  // Extract the relevant data from the input file (Tx)
  l1t::demo::BoardData inputsTx = l1t::demo::read(inputFileNameTx, l1t::demo::FileFormat::EMPv2);
  auto nChannelsTx = inputsTx.size();
  auto nFramesTx = inputsTx.begin()->second.size();
  std::cout << "Reading Tx file" << std::endl;
  std::cout << "Board from file: " << inputFileNameTx << std::endl;
  std::cout << "Board data name : " << inputsTx.name() << ", and number of channels are: " << nChannelsTx  << " with number of frames: " << nFramesTx << std::endl;
  std::cout << std::endl;

  // List of cluster words
  std::vector<std::map<int, uint64_t>> clusterFrames;
  size_t i_channel_tx = 0;
  for (size_t i_frame_tx=0; i_frame_tx < nFramesTx; ++i_frame_tx) {
    std::map<int, uint64_t> clusterFrame;
    for (const auto& channel_data: inputsTx) {
      if (i_channel_tx > 3) break; // Limit to 4 channels
      auto channel_frames = channel_data.second;
      frameWord = channel_frames[i_frame_tx].data.to_uint64();
      clusterFrame.insert(std::pair<int, uint64_t>(i_channel_tx, frameWord));
      i_channel_tx++;
    }
    clusterFrames.push_back(clusterFrame);
    i_channel_tx = 0; // Reset for the next frame
  }
  std::cout << "Cluster frames filled from Tx data." << std::endl;
  std::cout << std::endl;

  /*
  // Print out the cluster frames
  for (size_t i_frame = 0; i_frame < clusterFrames.size(); ++i_frame) {
    std::cout << "Frame " << i_frame << ": ";
    for (const auto& word : clusterFrames[i_frame]) {
      std::cout << std::hex << std::setw(16) << std::setfill('0') << word.second << " ";
    }
    std::cout << std::dec << std::endl;
  }
    */

  // Perform a frame count check
  if (accumulatorFrames.size() != clusterFrames.size()) {
    std::cerr << "Error: Number of frames in Rx and Tx data do not match!" << std::endl;
    return 2;
  }

  // Also the accumulator input data filestream
  std::ofstream outputAccumulInputFile(outputAccumulInputFileName);
  if (!outputAccumulInputFile.is_open()) {
    std::cerr << "Error: Could not open output file " << outputAccumulInputFileName << std::endl;
    return 5;
  }
  // Open the two filestreams for output
  std::ofstream outputFile(outputFileName);
  if (!outputFile.is_open()) {
    std::cerr << "Error: Could not open output file " << outputFileName << std::endl;
    return 3;
  }
  std::ofstream outputFileProp(outputFileNameProp);
  if (!outputFileProp.is_open()) {
    std::cerr << "Error: Could not open output file " << outputFileNameProp << std::endl;
    return 4;
  }
  
  outputAccumulInputFile << "FrameNumber,NumberOfTcs,TotE,CeeE,CeeECore,CeHEarly,SumW,NumberOfTcsW,"
                   << "SumW2,SumWZ,SumWRoZ,SumWPhi,SumWZ2,SumWRoZ2,SumWPhi2,LayerBits,satTC,shapeQ" << std::endl;
  outputFile << "FrameNumber,EmulWord1,FwWord1,EmulWord2,FwWord2,EmulWord3,FwWord3" << std::endl;
  outputFileProp << "FrameNumber,EmulE_T,FwE_T,EmulE_EM,FwE_EM,EmulGCTBits,FwGCTBits,"
                 << "EmulFractionInCE_E,FwFractionInCE_E,EmulFractionInCoreCE_E,FwFractionInCoreCE_E,"
                 << "EmulFractionInEarlyCE_E,FwFractionInEarlyCE_E,EmulFirstLayer,FwFirstLayer,"
                 << "EmulW_eta,FwW_eta,EmulW_phi,FwW_phi,EmulW_z,FwW_z,EmulN_TCs,FwN_TCs,"
                 << "EmulQualFlags,FwQualFlags,EmulSigma_E,FwSigma_E,EmulLastLayer,FwLastLayer,"
                 << "EmulShowerLength,FwShowerLength,EmulSigma_z,FwSigma_z,EmulSigma_phi,FwSigma_phi,"
                 << "EmulCoreShowerLength,FwCoreShowerLength,EmulSigma_eta,FwSigma_eta,"
                 << "EmulSigma_roz,FwSigma_roz" << std::endl;


  // Loop through each of the frames, produce the emulated cluster words and compare with the firmware words
  // Now use the accumulator input dataformat
  TPGBEDataformat::TcAccumulatorFW accmulInput(3);
  l1thgcfirmware::HGCalCluster_HW L1TOutputEmul;
  l1thgcfirmware::HGCalCluster_HW L1TOutputFW;
  //TPGStage2Emulation::Stage2 s2Clustering;
  TPGClusterProperties s2Clustering;

  std::cout <<"size of TPGStage2Emulation::TcAccumulator : " << sizeof(TPGStage2Emulation::TcAccumulator) << std::endl;
  std::cout <<"size of TPGBEDataformat::TcAccumulatorFW : " << sizeof(TPGBEDataformat::TcAccumulatorFW) << std::endl;
  std::cout <<"size of l1thgcfirmware::HGCalCluster_HW : " << sizeof(l1thgcfirmware::HGCalCluster_HW) << std::endl;

  //Set LUTs
  TPGStage2Configuration::ClusPropLUT cplut;
  cplut.readMuEtaLUT("input/stage2/configuration/mean_eta_LUT.csv");
  cplut.readSigmaEtaLUT("input/stage2/configuration/sigma_eta_LUT.csv");

  //Set LSBScales
  TPGLSBScales::TPGStage2ClusterLSB lsbScales;
  lsbScales.setMaxTCETbits(19);
  lsbScales.setMaxTCRoZbits(13);

  // Prepare s2Clustering object
  s2Clustering.setLSBScales(&lsbScales);
  s2Clustering.setClusPropLUT(&cplut);

  // Firmware objets
  ap_uint<l1thgcfirmware::HGCalCluster_HW::BITWIDTH_FIRSTWORD> firstw;
  ap_uint<l1thgcfirmware::HGCalCluster_HW::BITWIDTH_SECONDWORD> secondw;
  ap_uint<l1thgcfirmware::HGCalCluster_HW::BITWIDTH_THIRDWORD> thirdw;


  for (size_t i_frame = 0; i_frame < accumulatorFrames.size(); ++i_frame){
    // Early stopping condition due to offset
    if ((i_frame + offsetRx) > (nFramesTx - 1)){
      std::cout << "Rx + offset exceeds Tx length at frame: " << i_frame << std::endl;
      break;
    }

    // Emulation
    std::map<int, uint64_t> accumulatorFrameRx = accumulatorFrames[i_frame];
    accmulInput.setNumberOfTcs    ( accumulatorFrameRx.at(0) );
    accmulInput.setTotE           ( accumulatorFrameRx.at(1) );
    accmulInput.setCeeE           ( accumulatorFrameRx.at(2) );
    accmulInput.setCeeECore       ( accumulatorFrameRx.at(3) );
    accmulInput.setCeHEarly       ( accumulatorFrameRx.at(4) );
    accmulInput.setSumW           ( accumulatorFrameRx.at(5) );
    accmulInput.setNumberOfTcsW   ( accumulatorFrameRx.at(6) );
    accmulInput.setSumW2          ( accumulatorFrameRx.at(7) );
    accmulInput.setSumWZ          ( accumulatorFrameRx.at(8) );
    accmulInput.setSumWRoZ        ( accumulatorFrameRx.at(9) );
    accmulInput.setSumWPhi        ( accumulatorFrameRx.at(10) );
    accmulInput.setSumWZ2         ( accumulatorFrameRx.at(11) );
    accmulInput.setSumWRoZ2       ( accumulatorFrameRx.at(12) );
    accmulInput.setSumWPhi2       ( accumulatorFrameRx.at(13) );
    accmulInput.setLayerBits      ( accumulatorFrameRx.at(14) );
    accmulInput.setsatTC          ( accumulatorFrameRx.at(15) );
    accmulInput.setshapeQ         ( accumulatorFrameRx.at(16) );

    accmulInput.printdetail(0);
    accmulInput.printdetail(1);
    accmulInput.printmaxval();

    L1TOutputEmul.clear();

    s2Clustering.ClusterProperties(accmulInput, L1TOutputEmul);

    // Firmware
    std::map<int, uint64_t> clusterFrameTx = clusterFrames[i_frame + offsetRx];
    firstw = clusterFrameTx.at(0);
    secondw = clusterFrameTx.at(1);
    thirdw = clusterFrameTx.at(2);
    l1thgcfirmware::HGCalCluster_HW::unpack_firstWord(firstw, L1TOutputFW);
    l1thgcfirmware::HGCalCluster_HW::unpack_secondWord(secondw, L1TOutputFW);
    l1thgcfirmware::HGCalCluster_HW::unpack_thirdWord(thirdw, L1TOutputFW);

    // Print the outputs
    std::cout << "Emulated output for frame " << i_frame << ": " << std::endl;
    L1TOutputEmul.print();
    std::cout << "Firmware output for frame " << i_frame + offsetRx << ": " << std::endl;
    L1TOutputFW.print();
    std::cout << std::endl;

    // Word comparison
    uint64_t fw0 = firstw.to_uint64();
    uint64_t fw1 = secondw.to_uint64();
    uint64_t fw2 = thirdw.to_uint64();
    uint64_t emul0 = L1TOutputEmul.pack_firstWord();
    uint64_t emul1 = L1TOutputEmul.pack_secondWord();
    uint64_t emul2 = L1TOutputEmul.pack_thirdWord();

    // Accumulator input data output
    outputAccumulInputFile << i_frame << ","
    << std::dec << accmulInput.numberOfTcs() << ","
    << accmulInput.totE() << ","
    << accmulInput.ceeE() << ","
    << accmulInput.ceeECore() << ","
    << accmulInput.ceHEarly() << ","
    << accmulInput.sumW() << ","
    << accmulInput.numberOfTcsW() << ","
    << accmulInput.sumW2() << ","
    << accmulInput.sumWZ() << ","
    << accmulInput.sumWRoZ() << ","
    << accmulInput.sumWPhi() << ","
    << accmulInput.sumWZ2() << ","
    << accmulInput.sumWRoZ2() << ","
    << accmulInput.sumWPhi2() << ","
    << std::hex << std::setw(16) << std::setfill('0') << accmulInput.layerBits() << ","
    << std::dec << accmulInput.issatTC() << ","
    << std::dec << accmulInput.shapeQ()
    << std::endl;


    // Write to output file
    outputFile << i_frame << ","
    << std::hex << std::setw(16) << std::setfill('0') << emul0 << ","
    << std::hex << std::setw(16) << std::setfill('0') << fw0 << ","
    << std::hex << std::setw(16) << std::setfill('0') << emul1 << ","
    << std::hex << std::setw(16) << std::setfill('0') << fw1 << ","
    << std::hex << std::setw(16) << std::setfill('0') << emul2 << ","
    << std::hex << std::setw(16) << std::setfill('0') << fw2 << std::dec 
    << std::endl;
    
    // Property comparison (Note: w_phi is signed)
    outputFileProp << i_frame << ","
    << L1TOutputEmul.e.to_uint64() << "," << L1TOutputFW.e.to_uint64() << ","
    << L1TOutputEmul.e_em.to_uint64() << "," << L1TOutputFW.e_em.to_uint64() << ","
    << L1TOutputEmul.gctBits.to_uint64() << "," << L1TOutputFW.gctBits.to_uint64() << ","
    << L1TOutputEmul.fractionInCE_E.to_uint64() << "," << L1TOutputFW.fractionInCE_E.to_uint64() << ","
    << L1TOutputEmul.fractionInCoreCE_E.to_uint64() << "," << L1TOutputFW.fractionInCoreCE_E.to_uint64() << ","
    << L1TOutputEmul.fractionInEarlyCE_E.to_uint64() << "," << L1TOutputFW.fractionInEarlyCE_E.to_uint64() << ","
    << L1TOutputEmul.firstLayer.to_uint64() << "," << L1TOutputFW.firstLayer.to_uint64() << ","
    << L1TOutputEmul.w_eta.to_uint64() << "," << L1TOutputFW.w_eta.to_uint64() << ","
    << L1TOutputEmul.w_phi.to_int64() << "," << L1TOutputFW.w_phi.to_int64() << ","
    << L1TOutputEmul.w_z.to_uint64() << "," << L1TOutputFW.w_z.to_uint64() << ","
    << L1TOutputEmul.nTC.to_uint64() << "," << L1TOutputFW.nTC.to_uint64() << ","
    << L1TOutputEmul.qualFlags.to_uint64() << "," << L1TOutputFW.qualFlags.to_uint64() << ","
    << L1TOutputEmul.sigma_E.to_uint64() << "," << L1TOutputFW.sigma_E.to_uint64() << ","
    << L1TOutputEmul.lastLayer.to_uint64() << "," << L1TOutputFW.lastLayer.to_uint64() << ","
    << L1TOutputEmul.showerLength.to_uint64() << "," << L1TOutputFW.showerLength.to_uint64() << ","
    << L1TOutputEmul.sigma_z.to_uint64() << "," << L1TOutputFW.sigma_z.to_uint64() << ","
    << L1TOutputEmul.sigma_phi.to_uint64() << "," << L1TOutputFW.sigma_phi.to_uint64() << ","
    << L1TOutputEmul.coreShowerLength.to_uint64() << "," << L1TOutputFW.coreShowerLength.to_uint64() << ","
    << L1TOutputEmul.sigma_eta.to_uint64() << "," << L1TOutputFW.sigma_eta.to_uint64() << ","
    << L1TOutputEmul.sigma_roz.to_uint64() << "," << L1TOutputFW.sigma_roz.to_uint64()
    << std::endl;

  }

  outputAccumulInputFile.close();
  std::cout << "Accumulator input data written to: " << outputAccumulInputFileName << std::endl;

  outputFile.close();
  std::cout << "Comparison results written to: " << outputFileName << std::endl;

  outputFileProp.close();
  std::cout << "Property comparison results written to: " << outputFileNameProp << std::endl;



  return 0;
}