//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
//

#include "MobileApplication.h"
#include "BeaconFrame_m.h"

namespace smile {
namespace algorithm {
namespace whistle {

Define_Module(MobileApplication);

void MobileApplication::initialize(int stage)
{
  IdealApplication::initialize(stage);

  if (stage == inet::INITSTAGE_LOCAL) {
    const auto& frameTxIntervalParameter = par("frameTxInterval");
    frameTxInterval = SimTime(frameTxIntervalParameter.longValue(), SIMTIME_MS);
  }

  if (stage == inet::INITSTAGE_APPLICATION_LAYER) {
    sendFrame();
  }
}

void MobileApplication::handleIncommingMessage(cMessage* newMessage)
{
  std::unique_ptr<cMessage>{newMessage};
}

void MobileApplication::handleRxCompletionSignal(const smile::IdealRxCompletion& completion) {}

void MobileApplication::handleTxCompletionSignal(const smile::IdealTxCompletion& completion)
{
  sendFrame();
}

void MobileApplication::sendFrame()
{
  auto frame = createFrame<BeaconFrame>(inet::MACAddress::BROADCAST_ADDRESS);
  frame->setSequenceNumber(sequenceNumberGenerator);
  frame->setBitLength(10);
  frame->setEcho(false);
  sendDelayed(frame.release(), frameTxInterval, "out");

  sequenceNumberGenerator++;
}

}  // namespace whistle
}  // namespace algorithm
}  // namespace smile