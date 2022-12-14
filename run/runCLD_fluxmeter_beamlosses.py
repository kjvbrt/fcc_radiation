import os
from Gaudi.Configuration import INFO, DEBUG
from GaudiKernel.PhysicalConstants import pi, mm
from GaudiKernel.SystemOfUnits import GeV, tesla

from Configurables import ApplicationMgr
ApplicationMgr().EvtSel = 'NONE'
ApplicationMgr().EvtMax = 1
ApplicationMgr().OutputLevel = DEBUG
ApplicationMgr().StopOnSignal = True
ApplicationMgr().ExtSvc += ['RndmGenSvc']

## Data service
from Configurables import FCCDataSvc
data_service = FCCDataSvc("EventDataSvc")
data_service.OutputLevel = DEBUG
from Configurables import MDIReader
mdiconverter = MDIReader("MDIReader")
mdiconverter.GenParticles.Path = "allGenParticles"
mdiconverter.CrossingAngle = 0.015
mdiconverter.LongitudinalCut = 0
mdiconverter.InputType = "xtrack"
mdiconverter.BeamEnergy = 45.6
mdiconverter.OutputLevel = DEBUG
ApplicationMgr().ExtSvc += [data_service]
ApplicationMgr().TopAlg += [mdiconverter]

# Detector geometry
from Configurables import GeoSvc
geoservice = GeoSvc("GeoSvc")
# if FCC_DETECTORS is empty, this should use relative path to working directory
path_to_detector = os.environ.get("FCCDETECTORS", "")
detectors_to_use = [
    # 'Detector/DetFCCeeIDEA-LAr/compact/FCCee_DectMaster.xml',
    'Detector/DetFCCeeCLD/compact/FCCee_o2_v02/FCCee_o2_v02.xml',
]
# prefix all xmls with path_to_detector
geoservice.detectors = [os.path.join(path_to_detector, _det) for _det
                        in detectors_to_use]
geoservice.OutputLevel = INFO
ApplicationMgr().ExtSvc += [geoservice]


# Magnetic field
# from Configurables import SimG4ConstantMagneticFieldTool
# field = SimG4ConstantMagneticFieldTool("SimG4ConstantMagneticFieldTool")
# field.FieldComponentZ = -2 * tesla
# field.FieldOn = True
# field.FieldRMax = 3719 * mm
# field.FieldZMax = 3705 * mm
# field.IntegratorStepper = "ClassicalRK4"

# from Configurables import SimG4MagneticFieldFromMapTool
# field = SimG4MagneticFieldFromMapTool("SimG4MagneticFieldFromMapTool")
# field.MapFile = "/home/jsmiesko/FCC/fcc_radiation/input/fieldMapXYZ_120218.root"
# field.FieldOn = True
# field.IntegratorStepper = "ClassicalRK4"
# field.OutputLevel = DEBUG

# Geant4 service
# Configures the Geant simulation: geometry, physics list and user actions
from Configurables import SimG4Svc
# giving the names of tools will initialize the tools of that type
geantservice = SimG4Svc("SimG4Svc")
#geantservice.detector = "SimG4DD4hepDetector"
#geantservice.physicslist = "SimG4FtfpBert"
#geantservice.actions = "SimG4FullSimActions"
# geantservice.magneticField = field
# Fixed seed to have reproducible results, change it for each job if you split
# one production into several jobs
# Mind that if you leave Gaudi handle random seed and some job start within the
# same second (very likely) you will have duplicates
geantservice.randomNumbersFromGaudi = False
# geantservice.seedValue = 42424
# Range cut
# geantservice.g4PreInitCommands += ["/run/setCut 0.1 mm"]
ApplicationMgr().ExtSvc += [geantservice]


# Geant4 algorithm
# Translates EDM to G4Event, passes the event to G4, writes out outputs via
# tools and a tool that saves the calorimeter hits


# Detector readouts
from Configurables import SimG4Alg
from Configurables import SimG4SaveFluxHits
saveFluxTool = SimG4SaveFluxHits("saveFluxHits")
saveFluxTool.readoutNames = ["FluxPhiTheta"]
SimG4Alg("SimG4Alg").outputs += [saveFluxTool]

# next, create the G4 algorithm, giving the list of names of tools ("XX/YY")
from Configurables import SimG4PrimariesFromEdmTool
particle_converter = SimG4PrimariesFromEdmTool("EdmConverter")
# particle_converter.GenParticles.Path = "GenParticles"
particle_converter.GenParticles.Path = "allGenParticles"

from Configurables import SimG4Alg
geantsim = SimG4Alg("SimG4Alg")
geantsim.eventProvider = particle_converter
ApplicationMgr().TopAlg += [geantsim]

################ Output
from Configurables import PodioOutput
out = PodioOutput("out")
out.outputCommands = ["keep *"]
import uuid
out.filename = "output_fluxmeter_" + uuid.uuid4().hex[:12] + ".root"
ApplicationMgr().TopAlg += [out]

#CPU information
from Configurables import AuditorSvc, ChronoAuditor
chra = ChronoAuditor()
audsvc = AuditorSvc()
audsvc.Auditors = [chra]
geantsim.AuditExecute = True
out.AuditExecute = True

from Configurables import EventCounter
event_counter = EventCounter('event_counter')
event_counter.Frequency = 1
ApplicationMgr().TopAlg += [event_counter]
