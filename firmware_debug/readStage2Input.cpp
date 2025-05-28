#include <iostream>
#include <fstream>
#include "L1Trigger/DemonstratorTools/interface/utilities.h"

int main(int argc, char* argv[])
{   
  std::string inputFileName;
  std::string outputFileName;
  if (argc == 1){
    std::cout << "Using default input file: EMPStage2Input.txt" << std::endl;
    std::cout << "Using default output file: EMPStage2InputRead.txt" << std::endl;
    inputFileName = std::string("EMPStage2Input.txt");
    outputFileName = std::string("EMPStage2InputRead.txt");
  } 
  else if (argc == 2){
    std::cout << "Using default output file: EMPStage2InputRead.txt" << std::endl;
    inputFileName = std::string(argv[1]);
    outputFileName = std::string("EMPStage2InputRead.txt");
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
  // Note: Here, each frame is a TC accumulation, and each channel is a property of the accumulated value
  int i_channel = 0;
  for(const auto& channel_data: inputs){
    if (i_channel > 3) break;
    std::cout << "Channel: " << channel_data.first << std::endl;
    int i_frame = 0;
    int i_frame_in_packet = 0;
    int n_packets = 0;
    bool in_packet = true;
    int n_clusters = 0;
    for (const auto& frame : channel_data.second){
      // Find start of packet
      if (frame.startOfPacket){
        in_packet = true;
        n_packets++;
        i_frame_in_packet = 0;
        n_clusters = 0;
        std::cout <<
        "Start of packet: " << n_packets - 1 <<
        " at frame: " << i_frame <<
        std::endl;

        // In this case, the start of the packet is also the start of the accumulation
        switch (i_channel){
          case 0:
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

        i_frame_in_packet++;
        i_frame++;
      }

      // Find termination of packet (termination can come first from junk)
      else if (frame.endOfPacket){
        if (n_packets > 0){
          switch (i_channel){
            case 0:
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

        // Packet summary info 
        std::cout << 
        "End of packet: " << n_packets - 1 <<
        " at frame: " << i_frame <<
        ", frames in packet: " << i_frame_in_packet + 1 << 
        ", accumulated TCs: " << n_clusters <<
        std::endl;
        in_packet = false;

        i_frame_in_packet++;
        i_frame++;
      }

      // General word
      else{
        if (n_packets > 0){
          switch (i_channel){
            case 0:
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

        // Count the frame (and packet)
        if (in_packet){
          i_frame_in_packet++;
          i_frame++;
        }
        else {
          i_frame++;
        }
      }
    }

    i_channel++;
  }

  std::cout << std::endl;
  std::cout << "Reading accumulated data..." << std::endl;
  // Print out the accumulated data
  for (size_t i = 0; i < cluster_word1.size(); i++){
    int32_t ntcs = (cluster_word1[i]) & 0x3ff;
    std::cout <<
    "Accumulated TC " << i <<
    " frame: " << frame_number[i] <<
    " Accumulated TC number: " << cluster_number[i] <<
    " word: " << std::hex << std::setw(16) << std::setfill('0') << cluster_word1[i] <<
    " with nTCs word: " << std::hex << std::setw(5) << std::setfill('0') << ((cluster_word1[i]) & 0x3ff) << " = " << std::dec << ntcs <<
    std::endl;
  }

  // Write out the accumulated data
  std::ofstream outputFile(outputFileName);
  if (!outputFile.is_open()) {
    std::cerr << "Error opening output file: " << outputFileName << std::endl;
    return 3;
  }
  outputFile << "Entry number\tAccumulated TC number\tFrame number\tnTCs\tnTC word" << std::endl;
  for (size_t i = 0; i < cluster_word1.size(); i++){
    int32_t ntcs = (cluster_word1[i]) & 0x3ff;
    outputFile << 
    std::dec << i << "\t" <<
    cluster_number[i] << "\t" <<
    frame_number[i] << "\t" <<
    ntcs << "\t" <<
    std::hex << std::setw(16) << std::setfill('0') << cluster_word1[i] << std::dec <<
    std::endl;
  }

  outputFile.close();
  std::cout << "Wrote accumulated TC data to: " << outputFileName << std::endl;
  return 0;



}
