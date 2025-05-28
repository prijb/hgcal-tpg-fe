#include <iostream>
#include <fstream>
#include "L1Trigger/DemonstratorTools/interface/utilities.h"

int main(int argc, char* argv[])
{   
  std::string inputFileName;
  std::string outputFileName;
  if (argc == 1){
    std::cout << "Using default input file: EMPStage2Output.txt" << std::endl;
    std::cout << "Using default output file: EMPStage2OutputRead.txt" << std::endl;
    inputFileName = std::string("EMPStage2Output.txt");
    outputFileName = std::string("EMPStage2OutputRead.txt");
  } 
  else if (argc == 2){
    std::cout << "Using default output file: EMPStage2OutputRead.txt" << std::endl;
    inputFileName = std::string(argv[1]);
    outputFileName = std::string("EMPStage2OutputRead.txt");
  } 
  else{
    std::cout << "Using input file: " << argv[1] << std::endl;
    std::cout << "Using output file: " << argv[2] << std::endl;
    inputFileName = std::string(argv[1]);
    outputFileName = std::string(argv[2]);
  }

  l1t::demo::BoardData inputs = l1t::demo::read(inputFileName, l1t::demo::FileFormat::EMPv2);
  auto nChannels = inputs.size();
  auto firstChannel = inputs.begin();
  auto nFrames = firstChannel->second.size();

  std::vector<int> frame_number;
  std::vector<int> cluster_number;
  std::vector<uint64_t> cluster_word1;
  std::vector<uint64_t> cluster_word2;
  std::vector<uint64_t> cluster_word3;
  std::vector<uint64_t> cluster_word4;

  std::cout << "Filename : " << inputFileName << std::endl;
  std::cout << "Board data name : " << inputs.name() << std::endl;
  std::cout << "Number of channels : " << nChannels << std::endl;
  std::cout << "Number of frames : " << nFrames << std::endl;

  // Read the board data
  std::cout << "Reading board data..." << std::endl;
  
  // Fill the cluster words
  int i_channel = 0;
  for(const auto& channel_data: inputs){
    if (i_channel > 3) break;
    std::cout << "Channel: " << channel_data.first << std::endl;
    int i_frame = 0;
    int i_frame_in_packet = 0;
    int n_packets = 0;
    bool in_packet = true;
    int n_clusters = 0;
    for (const auto& frame : channel_data.second) {
      //if (i_frame > 200) break;
      
      // Find start of packet 
      if (frame.startOfPacket) {
        in_packet = true;
        n_packets++;
        i_frame_in_packet = 0;
        n_clusters = 0;
        std::cout <<
        "Start of packet: " << n_packets - 1 <<
        " at frame: " << i_frame <<
        std::endl;

        i_frame_in_packet++;
        i_frame++;
      }

      // Find termination of packet (termination can come first from junk)
      // Q. Does end of packet have a valid cluster?
      else if (frame.endOfPacket) {
        if (n_packets > 0){
          switch (i_channel){
            case 0:
              //std::cout << "Writing cluster word 0 of cluster " << n_clusters + 1
              //<< " at frame " << i_frame << std::endl;
              frame_number.push_back(i_frame);
              cluster_number.push_back(n_clusters);
              cluster_word1.push_back(frame.data.to_uint64());
              break;
            case 1:
              cluster_word2.push_back(frame.data.to_uint64());
              break;
            case 2:
              cluster_word3.push_back(frame.data.to_uint64());
              break;
            case 3:
              cluster_word4.push_back(frame.data.to_uint64());
              break;
            default:
              std::cout << "Error: channel number out of range" << std::endl;
          
          }
          // Count cluster if packet > 0
          n_clusters++;
        }
        // Packet summary info
        std::cout << 
        "End of packet: " << n_packets - 1 <<
        " at frame: " << i_frame <<
        ", frames in packet: " << i_frame_in_packet + 1 << 
        ", clusters: " << n_clusters <<
        std::endl;
        in_packet = false;

        i_frame_in_packet++;
        i_frame++;

      }

      // General word
      else{
        
        // Analyze packet if packet > 0
        if (n_packets > 0){
          // Cluster analysis
          // First 30 (+1 header) frames are towers which we don't care about
          if ((i_frame_in_packet > 30)){
            switch (i_channel){
              case 0:
                //std::cout << "Writing cluster word 0 of cluster " << n_clusters
                //<< " at frame " << i_frame << std::endl;
                frame_number.push_back(i_frame);
                cluster_number.push_back(n_clusters);
                cluster_word1.push_back(frame.data.to_uint64());
                break;
              case 1:
                cluster_word2.push_back(frame.data.to_uint64());
                break;
              case 2:
                cluster_word3.push_back(frame.data.to_uint64());
                break;
              case 3:
                cluster_word4.push_back(frame.data.to_uint64());
                break;
              default:
                std::cout << "Error: channel number out of range" << std::endl;
            }
            n_clusters++;
          }
        }

        // Count frames
        if (in_packet){
          i_frame_in_packet++;
          i_frame++;
        }
        else i_frame++;
      }

    }
      /*
      std::cout << 
      "Frame: " << i_frame << 
      ", valid: " << frame.valid <<
      ", strobe: " << frame.strobe <<
      ", startOfOrbit: " << frame.startOfOrbit <<
      ", startOfPacket: " << frame.startOfPacket <<
      ", endOfPacket: " << frame.endOfPacket <<
      ", data: 0x" << std::hex << std::setw(16) << std::setfill('0') << frame.data.to_uint64() <<
      std::dec << std::endl;
      */
    i_channel++;
  }

  std::cout << std::endl;
  std::cout << "Reading cluster data..." << std::endl;
  // Print out the cluster data
  for (size_t i = 0; i < cluster_word1.size(); i++){
    int32_t ntcs = (cluster_word2[i] >> 32) & 0x3ff;
    std::cout << 
    "Cluster " << i << 
    " frame: " << frame_number[i] <<
    " cluster: " << cluster_number[i] <<
    " word: " << std::hex << std::setw(16) << std::setfill('0') << cluster_word1[i] <<
    " " << std::hex << std::setw(16) << std::setfill('0') << cluster_word2[i] <<
    " " << std::hex << std::setw(16) << std::setfill('0') << cluster_word3[i] <<
    " " << std::hex << std::setw(16) << std::setfill('0') << cluster_word4[i] <<
    " with nTCs word: " << std::hex << std::setw(5) << std::setfill('0') << ((cluster_word2[i] >> 32) & 0x3ff) <<
    " = " << std::dec << ntcs <<
    std::endl;
  }

  // Write out the cluster data
  /*
  Format:
  Entry number | Cluster number | Frame number | nTCs | Cluster word 1 | Cluster word 2 | Cluster word 3
  */
  std::ofstream outputFile(outputFileName);
  if (!outputFile.is_open()) {
    std::cerr << "Error opening output file: " << outputFileName << std::endl;
    return 3;
  }
  outputFile << "Entry number\tCluster number\tFrame number\tnTCs\tCluster word 1\tCluster word 2\tCluster word 3\tCluster word 4" << std::endl;
  for (size_t i = 0; i < cluster_word1.size(); i++){
    int32_t ntcs = (cluster_word2[i] >> 32) & 0x3ff;
    outputFile << 
    std::dec << i << "\t" <<
    cluster_number[i] << "\t" <<
    frame_number[i] << "\t" <<
    ntcs << "\t" <<
    std::hex << std::setw(16) << std::setfill('0') << cluster_word1[i] << "\t" <<
    std::hex << std::setw(16) << std::setfill('0') << cluster_word2[i] << "\t" <<
    std::hex << std::setw(16) << std::setfill('0') << cluster_word3[i] << "\t" <<
    std::hex << std::setw(16) << std::setfill('0') << cluster_word4[i] <<
    std::dec << std::endl;
  }

  outputFile.close();
  std::cout << "Wrote cluster data to: " << outputFileName << std::endl;
  return 0;
}