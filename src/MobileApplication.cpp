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
#include <inet/common/ModuleAccess.h>
#include "BeaconFrame_m.h"
#include "CsvLoggerExtensions.h"

namespace smile {
namespace algorithm {
namespace whistle {

Define_Module(MobileApplication);

MobileApplication::~MobileApplication()
{
  if (frameTxTimerMessage) {
    cancelAndDelete(frameTxTimerMessage);
  }
}

void MobileApplication::initialize(int stage)
{
  IdealApplication::initialize(stage);

  if (stage == inet::INITSTAGE_LOCAL) {
    const auto& frameTxIntervalParameter = par("frameTxInterval");
    frameTxInterval = SimTime(frameTxIntervalParameter.longValue(), SIMTIME_MS);
  }

  if (stage == inet::INITSTAGE_APPLICATION_LAYER) {
    auto* mobilesLog = inet::getModuleFromPar<smile::Logger>(par("mobilesLoggerModule"), this, true);
    const auto entry = csv_logger::compose(getMacAddress(), getCurrentTruePosition(), frameTxInterval);
    mobilesLog->append(entry);

    beaconsLog = inet::getModuleFromPar<smile::Logger>(par("mobileBeaconsLoggerModule"), this, true);

    frameTxTimerMessage = new cMessage{"frameTxTimerMessage"};
    sendFrame();
    scheduleAt(clockTime() + frameTxInterval, frameTxTimerMessage);
  }
}

void MobileApplication::handleSelfMessage(cMessage* newMessage)
{
  sendFrame();
  scheduleAt(clockTime() + frameTxInterval, newMessage);
}

void MobileApplication::handleIncommingMessage(cMessage* newMessage)
{
  std::unique_ptr<cMessage>{newMessage};
}

void MobileApplication::handleRxCompletionSignal(const smile::IdealRxCompletion& completion)
{
  const auto frame = omnetpp::check_and_cast<const BeaconFrame*>(completion.getFrame());
  const auto entry = csv_logger::compose(getMacAddress(), completion, *frame);
  beaconsLog->append(entry);
}

void MobileApplication::handleTxCompletionSignal(const smile::IdealTxCompletion& completion)
{
  const auto frame = omnetpp::check_and_cast<const BeaconFrame*>(completion.getFrame());
  const auto entry = csv_logger::compose(getMacAddress(), completion, *frame);
  beaconsLog->append(entry);
}

void MobileApplication::sendFrame()
{
  auto frame = createFrame<BeaconFrame>(inet::MACAddress::BROADCAST_ADDRESS);
  frame->setSequenceNumber(sequenceNumberGenerator);
  frame->setBitLength(10);
  frame->setEcho(false);
  frame->setOriginNodeAddress(getMacAddress());
  sendDelayed(frame.release(), frameTxInterval, "out");

  sequenceNumberGenerator++;
}

}  // namespace whistle
}  // namespace algorithm
}  // namespace smile
