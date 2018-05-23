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
#include <inet/common/ModuleAccess.h>
#include "BeaconFrame_m.h"
#include "CsvLoggerExtensions.h"
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
    echoDelay = SimTime(echoDelayParameter.intValue(), SIMTIME_MS);
  }

  if (stage == inet::INITSTAGE_APPLICATION_LAYER) {
    auto* anchorsLog = inet::getModuleFromPar<Logger>(par("anchorsLoggerModule"), this, true);
    const auto entry = csv_logger::compose(getMacAddress(), getCurrentTruePosition(), baseAnchor, echoDelay);
    anchorsLog->append(entry);

    std::string handleName{"anchors_beacons"};
    beaconsLog = inet::getModuleFromPar<Logger>(par("anchorBeaconsLoggerModule"), this, true);
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
  echoFrame->setOriginNodeAddress(frame->getOriginNodeAddress());

  const auto delay = rxBeginClockTimestamp + echoDelay - clockTime();
  sendDelayed(echoFrame.release(), delay, "out");
}

void AnchorApplication::handleRxCompletionSignal(const IdealRxCompletion& completion)
{
  const auto frame = omnetpp::check_and_cast<const BeaconFrame*>(completion.getFrame());
  const auto entry = csv_logger::compose(getMacAddress(), completion, *frame);
  beaconsLog->append(entry);

  rxBeginClockTimestamp = completion.getOperationBeginClockTimestamp();
}

void AnchorApplication::handleTxCompletionSignal(const IdealTxCompletion& completion)
{
  const auto frame = omnetpp::check_and_cast<const BeaconFrame*>(completion.getFrame());
  const auto entry = csv_logger::compose(getMacAddress(), completion, *frame);
  beaconsLog->append(entry);
}

}  // namespace whistle
}  // namespace algorithm
}  // namespace smile
