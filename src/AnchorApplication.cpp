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

#include "AnchorApplication.h"
#include <inet/common/INETDefs.h>
#include "BeaconFrame_m.h"
#include "CsvLogger.h"
#include "utilities.h"

namespace smile {
namespace algorithm {
namespace whistle {

Define_Module(AnchorApplication);

void AnchorApplication::initialize(int stage)
{
  IdealApplication::initialize(stage);

  if (stage == inet::INITSTAGE_LOCAL) {
    const auto& baseAnchorParameter = par("baseAnchor");
    baseAnchor = baseAnchorParameter.boolValue();

    const auto& echoDelayParameter = par("echoDelay");
    echoDelay = SimTime(echoDelayParameter.longValue(), SIMTIME_MS);
  }

  if (stage == inet::INITSTAGE_PHYSICAL_ENVIRONMENT_2) {
    auto& logger = getLogger();
    const auto handle = logger.obtainHandle("anchors");
    const auto& nicDriver = getNicDriver();
    const auto& address = nicDriver.getMacAddress();
    const auto entry = csv_logger::compose(address, getCurrentTruePosition());
    logger.append(handle, entry);

    std::string handleName{"anchor_"};
    handleName += address.str();
    beaconsLog = logger.obtainHandle(handleName);
  }
}

void AnchorApplication::handleIncommingMessage(cMessage* newMessage)
{
  const auto frame = dynamic_unique_ptr_cast<BeaconFrame>(std::unique_ptr<cMessage>{newMessage});
  if (frame->getEcho()) {
    return;
  }

  if (!baseAnchor) {
    return;
  }

  auto echoFrame = createFrame<BeaconFrame>(inet::MACAddress::BROADCAST_ADDRESS);
  echoFrame->setSequenceNumber(frame->getSequenceNumber());
  echoFrame->setBitLength(10);
  echoFrame->setEcho(true);
  sendDelayed(echoFrame.release(), echoDelay, "out");
}

void AnchorApplication::handleRxCompletionSignal(const IdealRxCompletion& completion)
{
  const auto frame = omnetpp::check_and_cast<const BeaconFrame*>(completion.getFrame());
  const auto entry = csv_logger::compose(completion, frame->getSrc(), frame->getDest(), frame->getSequenceNumber());
  auto& logger = getLogger();
  logger.append(beaconsLog, entry);
}

void AnchorApplication::handleTxCompletionSignal(const IdealTxCompletion& completion)
{
  const auto frame = omnetpp::check_and_cast<const BeaconFrame*>(completion.getFrame());
  const auto entry = csv_logger::compose(completion, frame->getSrc(), frame->getDest(), frame->getSequenceNumber());
  auto& logger = getLogger();
  logger.append(beaconsLog, entry);
}

}  // namespace whistle
}  // namespace algorithm
}  // namespace smile
