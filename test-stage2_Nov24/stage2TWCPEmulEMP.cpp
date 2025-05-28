/**********************************************************************
 Created on : 11/03/2025
 Purpose    : Emulation of tower and CP together for multiple bxs
 Author     : Indranil Das, Research Associate, Imperial
 Email      : indranil.das@cern.ch | indra.ehep@gmail.com
**********************************************************************/
#include <iostream>
#include "L1Trigger/DemonstratorTools/interface/utilities.h"

#include "TPGBEDataformat.hh"
#include "Stage2.hh"

#include "TPGStage2Configuration.hh"

int main(int argc, char** argv)
{
  //CaptureStage2_250214_1137 + EMPStage2Input_6Bxs_96lpGBTs_CEE+1_CEH+2_CP.txt
  //CaptureStage2_250314_1218 + EMPStage2Input_6Bxs_96lpGBTs_CEE+1_CEH+2_VBF_ClusProp_2025-03-12.txt
  // ===============================================
  std::string board_config = "input/stage2/configuration/Stage2Configuration.yaml" ;
  //std::string board_config = "input/stage2/firmware-data/CaptureStage2_250314_1218/Stage2Configuration.yaml" ;
  //std::string board_config = "input/stage2/firmware-data/CaptureStage2_250328_1136/Stage2Configuration.yaml" ;
  //std::string board_config = "input/stage2/firmware-data/CaptureStage2_250321_1305/Stage2Configuration.yaml" ;
  //std::string board_config = "../hgcal-tpg-fe-data/local-input/stage2/firmware-data/vbf_Captures/CaptureStage2_250404_1118/Stage2Configuration.yaml" ;

  TPGStage2Configuration::Stage2Board sb;
  sb.readConfigYaml(board_config.c_str());
  sb.print();
  
  TPGBEDataformat::TcAccumulatorFW accmulInput(3); //3 stands for k=3
  
  TPGStage2Configuration::ClusPropLUT cplut;
  cplut.readMuEtaLUT("input/stage2/configuration/mean_eta_LUT.csv");
  cplut.readSigmaEtaLUT("input/stage2/configuration/sigma_eta_LUT.csv");

  //std::string inputFileName = "input/stage2/firmware-data/CaptureStage2_250314_1218/EMPStage2Input_6Bxs_96lpGBTs_CEE+1_CEH+2_VBF_ClusProp_2025-03-12.txt";
  //std::string inputFileName = "EMPStage2Input_6Bxs_96lpGBTs_CEE+1_CEH+2_VBF_FixedPointCheck_2025-03-21.txt";
  //std::string inputFileName = "EMPStage2Input_6Bxs_96lpGBTs_CEE+1_CEH+2_VBF_SaturationCheck_2025-03-28.txt";
  //std::string inputFileName = "input/stage2/firmware-data/CaptureStage2_250321_1305/rx_summary.txt";
  std::string inputFileName = argv[1] ;
  std::string outputFileName = argv[2] ;
  
  l1t::demo::BoardData inputs = l1t::demo::read( inputFileName, l1t::demo::FileFormat::EMPv2 );
  auto nChannels = inputs.size();
  const size_t numWordsBx = 162;
  const size_t nofBx = 6;
  std::vector<TPGBEDataformat::Stage1ToStage2Data> vS12[nofBx];
  std::vector<TPGBEDataformat::Stage2DataLong> vS12L[nofBx];
  
  std::cout << "Board data name : " << inputs.name() << ", and number of channels are: " << nChannels  << std::endl;
  for ( const auto& channel : inputs ) {
    //std::cout << "Data on channel : " << channel.first << std::endl;
    unsigned int iFrame = 0;
    int ibx = 0;
    int s2i = 0;
    int s2il = 0;
    TPGBEDataformat::Stage1ToStage2Data s2InputBx ;
    TPGBEDataformat::Stage2DataLong s2LInputBx ; 
    for ( const auto& frame : channel.second ) {
      //std::cout << frame.startOfOrbit << frame.startOfPacket << frame.endOfPacket << frame.valid << " " << std::hex << frame.data << std::dec << std::endl;
      //if(iFrame%numWordsBx==0) s2InputBx = new TPGBEDataformat::Stage1ToStage2Data();
      s2LInputBx.setData(s2il, frame.data);
      s2il++;
      if(frame.valid and iFrame%3<=1){
	s2InputBx.setData(s2i, frame.data);
	s2i++;
      }
      iFrame++;
      if(iFrame%numWordsBx==0) {
	vS12L[ibx].push_back(s2LInputBx);
	s2il = 0;
	s2LInputBx.reset();
	vS12[ibx].push_back(s2InputBx);
	s2i = 0;
	s2InputBx.reset();
	ibx++;
	//delete s2InputBx;
      }
    }//loop over frames of a given channel
      
  }//loop over channels
  
  std::cout << "Nof links for Bx1 : " << vS12[0].size() << std::endl;
  std::cout << "Nof links for Bx2 : " << vS12[1].size() << std::endl;
  
  std::cout << "Nof links for Bx1 in Stage2L: " << vS12L[0].size() << std::endl;
  std::cout << "Nof links for Bx2 in Stage2L: " << vS12L[1].size() << std::endl;
  
  TPGStage2Emulation::Stage2 stage2TowerEmul;
  stage2TowerEmul.setConfiguration(&sb);
  stage2TowerEmul.setAccuOutput(&accmulInput);
  stage2TowerEmul.setClusPropLUT(&cplut);
  
  TPGBEDataformat::Stage2ToL1TData s2OutputBx[nofBx] ; 
  for(int ibx=0;ibx<nofBx;ibx++){
    stage2TowerEmul.run(vS12[ibx],vS12L[ibx]);
    for(unsigned phi(0);phi<24;phi++) {
      for(unsigned eta(0);eta<20;eta++) {
	//std::cout << "stage2TowerEmulEMP.exe:  eta: " << eta << ", phi : " << phi << ", towerdata0:" << stage2TowerEmul.getTowerData(0,eta,phi) << ", towerdata1:" << stage2TowerEmul.getTowerData(1,eta,phi) <<", value: 0x" << std::hex << stage2TowerEmul.getTowerOutput(eta,phi) << std::dec << std::endl;
	s2OutputBx[ibx].setTowerLinkData(eta, phi, stage2TowerEmul.getTowerOutput(eta,phi));
      }
    }
    for(unsigned il(0);il<4;il++) {
      for(unsigned iw(0);iw<108;iw++) {
	s2OutputBx[ibx].setData(il, iw+31, stage2TowerEmul.getClusterOutput(0, iw, il));
      }
      for(unsigned iw(0);iw<23;iw++) {
	s2OutputBx[ibx].setData(il, iw+31+108, 0x0);
      }
    }
    
  }//bx loop

  //Write EMP output
  l1t::demo::BoardData boardData("L1TBoard");
  
  // Number of frames
  const size_t l1tnumWordsBx = numWordsBx;
  
  // Channels to define
  std::vector<size_t> channels;
  for (int ich = 4 ; ich <= 15 ; ich++) channels.push_back(ich);

  uint64_t emptydata = 0;
  for (size_t channel : channels) {
    // Create a Channel object (vector of Frames)
    l1t::demo::BoardData::Channel channelData;
    int ilink = channel%4;
    for (size_t ibx = 0; ibx < nofBx; ++ibx) {
      s2OutputBx[ibx].setBxId(ibx);
      s2OutputBx[ibx].setLinkId(channel);
      s2OutputBx[ibx].setBit(ilink,0,52);
      for (size_t i = 0; i < l1tnumWordsBx; ++i) {
	// Create a Frame object and populate it
	l1t::demo::Frame frame;
	//frame.data = (i==0)?emptydata:s2OutputBx[ibx].getData(ilink,i-1);
	frame.data = (i==0)?s2OutputBx[ibx].getHeader(ilink):s2OutputBx[ibx].getData(ilink,i);
	frame.valid = (i <= 138) ;//((i <= 30) or ((i-1)%3<=1));//(i <= 30);
	frame.startOfOrbit = false;
	frame.startOfPacket = (i == 0);
	frame.endOfPacket = (i == (l1tnumWordsBx-1));

	// Add the frame to the channel data
	channelData.push_back(frame);       
      }//loop 30 words      
    }//ibx

    // Add the channel to the BoardData object
    boardData.add(channel, channelData);
  }
  
  // Write the BoardData to file in EMP format
  //write(boardData, "EMPStage2Output.txt", l1t::demo::FileFormat::EMPv2);
  write(boardData, outputFileName, l1t::demo::FileFormat::EMPv2);

    
  return true;

}
