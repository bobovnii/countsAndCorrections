import ROOT
import numpy as np

from math import sqrt
attic = []


ROOT.gStyle.SetOptStat(0)


etaCuts = {
			"Barrel":"abs(eta1) < 1.4 && abs(eta2) < 1.4",
			"Endcap":"(((abs(eta1) < 1.4 || abs(eta1) > 1.6) && (abs(eta2) < 1.4 || abs(eta2) > 1.6)) && 1.6 <= TMath::Max(abs(eta1),abs(eta2)))",
			"BothEndcap":"abs(eta1) > 1.6 && abs(eta2) > 1.6",
			"Inclusive":"abs(eta1) < 2.4 && abs(eta2) < 2.4 && ((abs(eta1) < 1.4 || abs(eta1) > 1.6) && (abs(eta2) < 1.4 || abs(eta2) > 1.6))"
			}


def readTreeFromFile(path, dileptonCombination):
	"""
	helper functionfrom argparse import ArgumentParser
	path: path to .root file containing simulated events
	dileptonCombination: EMu, EMu, or EMu for electron-electron, electron-muon, or muon-muon events

	returns: tree containing events for on sample and dileptonCombination
	"""
	from ROOT import TChain
	result = TChain()
	result.Add("%s/cutsV23DileptonFinalTrees/%sDileptonTree"%(path, dileptonCombination))
	return result
def readTreeFromFileV22(path, dileptonCombination):
	"""
	helper functionfrom argparse import ArgumentParser
	path: path to .root file containing simulated events
	dileptonCombination: EMu, EMu, or EMu for electron-electron, electron-muon, or muon-muon events

	returns: tree containing events for on sample and dileptonCombination
	"""
	from ROOT import TChain
	result = TChain()
	result.Add("%s/cutsV22DileptonFinalTrees/%sDileptonTree"%(path, dileptonCombination))
	return result
	
def getFilePathsAndSampleNames(path):
	"""
	helper function
	path: path to directory containing all sample files

	returns: dict of smaple names -> path of .root file (for all samples in path)
	"""
	result = []
	from glob import glob
	from re import match
	result = {}
	for filePath in glob("%s/sw538*.root"%path):
		sampleName = match(".*sw538v.*\.processed.*\.(.*).root", filePath).groups()[0]
		#for the python enthusiats: yield sampleName, filePath is more efficient here :)
		result[sampleName] = filePath
	return result
	
def totalNumberOfGeneratedEvents(path):
	"""
	path: path to directory containing all sample files

	returns dict samples names -> number of simulated events in source sample
	        (note these include events without EMu EMu EMu signature, too )
	"""
	from ROOT import TFile
	result = {}
	for sampleName, filePath in getFilePathsAndSampleNames(path).iteritems():
		rootFile = TFile(filePath, "read")
		result[sampleName] = rootFile.FindObjectAny("analysis paths").GetBinContent(1)
	return result
	
def readTrees(path, dileptonCombination):
	"""
	path: path to directory containing all sample files
    dileptonCombination: "EMu", "EMu", or pyroot"EMu" for electron-electron, electron-muon, or muon-muon events

	returns: dict of sample names ->  trees containing events (for all samples for one dileptonCombination)
	"""
	result = {}
	print (path)
	for sampleName, filePath in getFilePathsAndSampleNames(path).iteritems():
		
		result[sampleName] = readTreeFromFile(filePath, dileptonCombination)
		
	return result
	
def readTreesV22(path, dileptonCombination):
	"""
	path: path to directory containing all sample files
    dileptonCombination: "EMu", "EMu", or pyroot"EMu" for electron-electron, electron-muon, or muon-muon events

	returns: dict of sample names ->  trees containing events (for all samples for one dileptonCombination)
	"""
	result = {}
	print (path)
	for sampleName, filePath in getFilePathsAndSampleNames(path).iteritems():
		
		result[sampleName] = readTreeFromFileV22(filePath, dileptonCombination)
		
	return result
	
	
def createHistoFromTree(tree, variable, weight, nBins, firstBin, lastBin, nEvents = -1):
	"""
	tree: tree to create histo from)
	variable: variable to plot (must be a branch of the tree)
	weight: weights to apply (e.g. "var1*(var2 > 15)" will use weights from var1 and cut on var2 > 15
	nBins, firstBin, lastBin: number of bins, first bin and last bin (same as in TH1F constructor)
	nEvents: number of events to process (-1 = all)
	"""
	from ROOT import TH1F
	from random import randint
	from sys import maxint
	if nEvents < 0:
		nEvents = maxint
	#make a random name you could give something meaningfull here,
	#but that would make this less readable
	name = "%x"%(randint(0, maxint))
	result = TH1F(name, "", nBins, firstBin, lastBin)
	result.Sumw2()
	tree.Draw("%s>>%s"%(variable, name), weight, "goff", nEvents)
	return result
	
def create2DHistoFromTree(tree, variable, variable2, weight, nBins, firstBin, lastBin, nBins2, firstBin2, lastBin2, nEvents = -1):
	"""
	tree: tree to create histo from)
	variable: variable to plot (must be a branch of the tree)
	weight: weights to apply (e.g. "var1*(var2 > 15)" will use weights from var1 and cut on var2 > 15
	nBins, firstBin, lastBin: number of bins, first bin and last bin (same as in TH1F constructor)
	nEvents: number of events to process (-1 = all)
	"""
	from ROOT import TH2F
	from random import randint
	from sys import maxint
	if nEvents < 0:
		nEvents = maxint
	#make a random name you could give something meaningfull here,
	#but that would make this less readable
	name = "%x"%(randint(0, maxint))
	result = TH2F(name, "", nBins, firstBin, lastBin,nBins2, firstBin2, lastBin2)
	result.Sumw2()
	tree.Draw("%s:%s>>%s"%(variable, variable2, name), weight, "goff", nEvents)
	return result
	
	
def setTDRStyle():
	from ROOT import TStyle
	from ROOT import kWhite
	from ROOT import kTRUE
	tdrStyle =  TStyle("tdrStyle","Style for P-TDR")
	
	# For the canvas:
	tdrStyle.SetCanvasBorderMode(0)
	tdrStyle.SetCanvasColor(kWhite)
	# For the canvas:
	tdrStyle.SetCanvasBorderMode(0)
	tdrStyle.SetCanvasColor(kWhite)
	tdrStyle.SetCanvasDefH(600) #Height of canvas
	tdrStyle.SetCanvasDefW(600)#Width of canvas
	tdrStyle.SetCanvasDefX(0)  #POsition on screen
	tdrStyle.SetCanvasDefY(0)
	
	# For the Pad:
	tdrStyle.SetPadBorderMode(0)
	# tdrStyle->SetPadBorderSize(Width_t size = 1);
	tdrStyle.SetPadColor(kWhite)
	tdrStyle.SetPadGridX(0)
	tdrStyle.SetPadGridY(0)
	tdrStyle.SetGridColor(0)
	tdrStyle.SetGridStyle(3)
	tdrStyle.SetGridWidth(1)
	
	# For the frame:
	tdrStyle.SetFrameBorderMode(0)
	tdrStyle.SetFrameBorderSize(1)
	tdrStyle.SetFrameFillColor(0)
	tdrStyle.SetFrameFillStyle(0)
	tdrStyle.SetFrameLineColor(1)
	tdrStyle.SetFrameLineStyle(1)
	tdrStyle.SetFrameLineWidth(1)
	
	# For the histo:
	# tdrStyle->SetHistFillColor(1);
	# tdrStyle->SetHistFillStyle(0);
	tdrStyle.SetHistLineColor(1)
	tdrStyle.SetHistLineStyle(0)
	tdrStyle.SetHistLineWidth(1)
	# tdrStyle->SetLegoInnerR(Float_t rad = 0.5);
	# tdrStyle->SetNumberContours(Int_t number = 20);
	
	tdrStyle.SetEndErrorSize(2)
	#  tdrStyle->SetErrorMarker(20);
	tdrStyle.SetErrorX(0.)
	
	tdrStyle.SetMarkerStyle(20)
	
	#For the fit/function:
	tdrStyle.SetOptFit(1)
	tdrStyle.SetFitFormat("5.4g")
	tdrStyle.SetFuncColor(2)
	tdrStyle.SetFuncStyle(1)
	tdrStyle.SetFuncWidth(1)
	
	#For the date:
	tdrStyle.SetOptDate(0)
	# tdrStyle->SetDateX(Float_t x = 0.01);
	# tdrStyle->SetDateY(Float_t y = 0.01);
	
	# For the statistics box:
	tdrStyle.SetOptFile(0)
	tdrStyle.SetOptStat("emr") # To display the mean and RMS:   SetOptStat("mr");
	tdrStyle.SetStatColor(kWhite)
	tdrStyle.SetStatFont(42)
	tdrStyle.SetStatFontSize(0.025)
	tdrStyle.SetStatTextColor(1)
	tdrStyle.SetStatFormat("6.4g")
	tdrStyle.SetStatBorderSize(1)
	tdrStyle.SetStatH(0.1)
	tdrStyle.SetStatW(0.15)
	# tdrStyle->SetStatStyle(Style_t style = 100.1);
	# tdrStyle->SetStatX(Float_t x = 0);
	# tdrStyle->SetStatY(Float_t y = 0);
	
	# Margins:
	tdrStyle.SetPadTopMargin(0.05)
	tdrStyle.SetPadBottomMargin(0.13)
	tdrStyle.SetPadLeftMargin(0.13)
	tdrStyle.SetPadRightMargin(0.175)
	
	# For the Global title:
	tdrStyle.SetOptTitle(0)
	tdrStyle.SetTitleFont(42)
	tdrStyle.SetTitleColor(1)
	tdrStyle.SetTitleTextColor(1)
	tdrStyle.SetTitleFillColor(10)
	tdrStyle.SetTitleFontSize(0.05)
	# tdrStyle->SetTitleH(0); # Set the height of the title box
	# tdrStyle->SetTitleW(0); # Set the width of the title box
	# tdrStyle->SetTitleX(0); # Set the position of the title box
	# tdrStyle->SetTitleY(0.985); # Set the position of the title box
	# tdrStyle->SetTitleStyle(Style_t style = 100.1);
	# tdrStyle->SetTitleBorderSize(2);
	
	# For the axis titles:
	tdrStyle.SetTitleColor(1, "XYZ")
	tdrStyle.SetTitleFont(42, "XYZ")
	tdrStyle.SetTitleSize(0.06, "XYZ")
	# tdrStyle->SetTitleXSize(Float_t size = 0.02); # Another way to set the size?
	# tdrStyle->SetTitleYSize(Float_t size = 0.02);
	tdrStyle.SetTitleXOffset(0.9)
	tdrStyle.SetTitleYOffset(1.0)
	# tdrStyle->SetTitleOffset(1.1, "Y"); # Another way to set the Offset
	
	# For the axis labels:
	tdrStyle.SetLabelColor(1, "XYZ")
	tdrStyle.SetLabelFont(42, "XYZ")
	tdrStyle.SetLabelOffset(0.007, "XYZ")
	tdrStyle.SetLabelSize(0.05, "XYZ")
	
	# For the axis:
	tdrStyle.SetAxisColor(1, "XYZ")
	tdrStyle.SetStripDecimals(kTRUE)
	tdrStyle.SetTickLength(0.03, "XYZ")
	tdrStyle.SetNdivisions(408, "XYZ")
	
	#~ tdrStyle->SetNdivisions(510, "XYZ");
	tdrStyle.SetPadTickX(1)  # To get tick marks on the opposite side of the frame
	tdrStyle.SetPadTickY(1)
	
	# Change for log plots:
	tdrStyle.SetOptLogx(0)
	tdrStyle.SetOptLogy(0)
	tdrStyle.SetOptLogz(0)
	
	# Postscript options:
	tdrStyle.SetPaperSize(20.,20.);
	# tdrStyle->SetLineScalePS(Float_t scale = 3);
	# tdrStyle->SetLineStyleString(Int_t i, const char* text);
	# tdrStyle->SetHeaderPS(const char* header);
	# tdrStyle->SetTitlePS(const char* pstitle);
	
	#tdrStyle->SetBarOffset(Float_t baroff = 0.5);
	#tdrStyle->SetBarWidth(Float_t barwidth = 0.5);
	#tdrStyle->SetPaintTextFormat(const char* format = "g");
	tdrStyle.SetPalette(1)
	#tdrStyle->SetTimeOffset(Double_t toffset);
	#tdrStyle->SetHistMinimumZero(kTRUE);
	
	
	
	
	ROOT.gROOT.ForceStyle()
	
	tdrStyle.cd()


def plotBlockComparison(treeBlockA,treeBlockB,variable,additionalCut,nBins,firstBin,lastBin,labelX,labelY,suffix,log=False,signal=False):	


	hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
	plotPad = ROOT.TPad("plotPad","plotPad",0,0.3,1,1)
	ratioPad = ROOT.TPad("ratioPad","ratioPad",0,0.,1,0.3)
	setTDRStyle()		
	plotPad.UseCurrentStyle()
	ratioPad.UseCurrentStyle()
	plotPad.Draw()	
	ratioPad.Draw()	
	plotPad.cd()	

	legend = TLegend(0.5, 0.55, 0.8, 0.95)
	legend.SetFillStyle(0)
	legend.SetBorderSize(1)
	

	
	

	minMll = 20

	ROOT.gStyle.SetOptStat(0)
	Cutlabel = ROOT.TLatex()
	Cutlabel.SetTextAlign(12)
	Cutlabel.SetTextSize(0.03)
	Labelin = ROOT.TLatex()
	Labelin.SetTextAlign(12)
	Labelin.SetTextSize(0.07)
	Labelin.SetTextColor(ROOT.kRed+2)
	Labelout = ROOT.TLatex()
	Labelout.SetTextAlign(12)
	Labelout.SetTextSize(0.07)
	Labelout.SetTextColor(ROOT.kBlack)



	
	EMuhistBlockA = createHistoFromTree(treeBlockA,  variable, additionalCut, nBins, firstBin, lastBin, -1)

	EMuhistBlockB = createHistoFromTree(treeBlockB,  variable, additionalCut, nBins, firstBin, lastBin, -1)
	
	EMuhistBlockB.Scale(9.2/10.4)
	print EMuhistBlockA.Integral()
	print EMuhistBlockB.Integral()
	EMuhistBlockA.SetMarkerStyle(21)
	EMuhistBlockB.SetMarkerStyle(22)
	EMuhistBlockA.SetMarkerColor(ROOT.kGreen+3)
	EMuhistBlockB.SetMarkerColor(ROOT.kBlack)
	EMuhistBlockA.SetLineColor(ROOT.kGreen+3)
	EMuhistBlockB.SetLineColor(ROOT.kBlack)
	
	if log: 
		yMin=0.1
		yMax = max(EMuhistBlockA.GetBinContent(EMuhistBlockA.GetMaximumBin()),EMuhistBlockB.GetBinContent(EMuhistBlockB.GetMaximumBin()))*10
		plotPad.SetLogy()
	else: 
		yMin=0
		yMax = max(EMuhistBlockA.GetBinContent(EMuhistBlockA.GetMaximumBin()),EMuhistBlockB.GetBinContent(EMuhistBlockB.GetMaximumBin()))*1.5
	hCanvas.DrawFrame(firstBin,yMin,lastBin,yMax,"; %s ; %s" %(labelX,labelY))

	EMuhistBlockA.Draw("samep")
	EMuhistBlockB.Draw("samep")
	
	legend.AddEntry(EMuhistBlockA,"First 9.2 fb^{-1}","p")	
	legend.AddEntry(EMuhistBlockB,"Second 10.4 fb^{-1} scaled","p")
	#~ 
	latex = ROOT.TLatex()
	latex.SetTextSize(0.043)
	latex.SetTextFont(42)
	latex.SetNDC(True)
	latex.DrawLatex(0.13, 0.95, "CMS Preliminary,    #sqrt{s} = 8 TeV,     #scale[0.6]{#int}Ldt = 9.2-10.4 fb^{-1}")
	#~ 
		
	legend.Draw("same")
	
	ratioPad.cd()

	ratioGraphs =  ratios.RatioGraph(EMuhistBlockA,EMuhistBlockB, firstBin, lastBin,title="Bl. A / Bl. B",yMin=0.0,yMax=2,ndivisions=10,color=ROOT.kGreen+3,adaptiveBinning=0.25)

	ratioGraphs.draw(ROOT.gPad,True,False,True,chi2Pos=0.8)
	if signal:
		name = "OFUnblinding_SignalRegion_%s_%s.pdf"
	else:
		name = "OFUnblinding_Inclusive_%s_%s.pdf"
	if variable == "p4.M()":
		
		hCanvas.Print(name%(suffix,"Mll"))
	else:		
		hCanvas.Print(name%(suffix,variable))	
		hCanvas.Clear()
if (__name__ == "__main__"):
	setTDRStyle()
	path = "/home/jan/Trees/sw538v0477/"
	from sys import argv
	import pickle	
	from ROOT import TCanvas, TPad, TH1F, TH1I, THStack, TLegend, TF1
	import ratios

	
	ptCut = "pt1 > 20 && pt2 > 20"#(pt1 > 10 && pt2 > 20 || pt1 > 20 && pt2 > 10)
	ptCutLabel = "20"#"20(10)"
	variable = "p4.M()"
	cuts = "weight*(chargeProduct < 0 && %s  && abs(eta1) < 2.4 && abs(eta2) < 2.4 && deltaR > 0.3 && ((abs(eta1) < 1.4 || abs(eta1) > 1.6) && (abs(eta2) < 1.4 || abs(eta2) > 1.6)))"%(ptCut)


	SampleNames = ["TTJets_MGDecays_madgraph_Summer12","ZJets_madgraph_Summer12","SUSY_SimplifiedModel_Madgraph_BR50_mb_600_mn2_200_mn1_130_Summer12_FastSim"]
	names = {"TTJets_MGDecays_madgraph_Summer12":"t#bar{t} Simulation","ZJets_madgraph_Summer12":"Drell-Yan + jets Simulation","SUSY_SimplifiedModel_Madgraph_BR50_mb_600_mn2_200_mn1_130_Summer12_FastSim":"SUSY"}
	fileNames = {"TTJets_MGDecays_madgraph_Summer12":"ttbar","ZJets_madgraph_Summer12":"DY","SUSY_SimplifiedModel_Madgraph_BR50_mb_600_mn2_200_mn1_130_Summer12_FastSim":"SUSY"}
	xSecs =  {"TTJets_MGDecays_madgraph_Summer12":22.4,"ZJets_madgraph_Summer12":3532.8,"SUSY_SimplifiedModel_Madgraph_BR50_mb_600_mn2_200_mn1_130_Summer12_FastSim":0.5}
	
	eventCounts = totalNumberOfGeneratedEvents(path)	

	for SampleName in SampleNames:

		eeTrees = readTrees(path, "EE")	
		mmTrees = readTrees(path, "MuMu")	
		emTrees = readTrees(path, "EMu")	
		for name, tree in eeTrees.iteritems():
			if name == SampleName:
				eeHist = create2DHistoFromTree(tree, "nJets","met", cuts, 100, 0, 500, 20,-0.5,19.5 ,nEvents = -1)
				#~ eeHist.Scale(1./eeHist.GetEntries())
		for name, tree in mmTrees.iteritems():
			if name == SampleName:
				mmHist = create2DHistoFromTree(tree, "nJets","met", cuts, 100, 0, 500 ,20,-0.5,19.5	, nEvents = -1)
				#~ mmHist.Scale(1./mmHist.GetEntries())
		for name, tree in emTrees.iteritems():
			if name == SampleName:
				emHist = create2DHistoFromTree(tree, "nJets","met", cuts, 100, 0, 500,20,-0.5,19.5	, nEvents = -1)
				#~ emHist.Scale(1./emHist.GetEntries())

		eeHist.Add(mmHist.Clone(""))
		eeHist.Add(emHist.Clone(""))
		eeHist.Scale(xSecs[SampleName]*19800/eventCounts[SampleName])
		hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
		plotPad = ROOT.TPad("plotPad","plotPad",0,0,1,1)
		#~ ratioPad = ROOT.TPad("ratioPad","ratioPad",0,0.,1,0.3)
		setTDRStyle()		
		plotPad.UseCurrentStyle()
		#~ ratioPad.UseCurrentStyle()
		plotPad.Draw()	
		#~ ratioPad.Draw()	
		#~ plotPad.cd()	

		legend = TLegend(0.45, 0.77, 0.8, 0.92)
		legend.SetFillStyle(0)
		legend.SetBorderSize(0)
		
		
		
		yMin=0
		yMax = max(eeHist.GetBinContent(eeHist.GetMaximumBin()),emHist.GetBinContent(mmHist.GetMaximumBin()))*1.5
		plotPad.DrawFrame(1,-0.5,300,12.5,"; %s ; %s" %("E_{T}^{miss} [GeV]","N_{Jets}"))
		ROOT.gStyle.SetOptStat(0)
		ROOT.gPad.SetLogz()
		eeHist.SetLineColor(ROOT.kRed)
		#~ eeHist.SetLineColor(ROOT.kRed)
		fakeHist = ROOT.TH1F()
		fakeHist.SetLineColor(ROOT.kWhite)
		legend.SetHeader("%s"%names[SampleName])
		#~ legend.AddEntry(eeHist,"e^{#pm}e^{#mp} + #mu^{#pm}#mu^{#mp}","l")
		#~ legend.AddEntry(mmHist,"e^{#pm}#mu^{#mp}","l")
		
		eeHist.Draw("samecolz")
		#~ mmHist.Draw("samehist")

		ROOT.gPad.RedrawAxis()
		
		line1 = ROOT.TLine(150,1.5,300,1.5)
		line2 = ROOT.TLine(100,2.5,100,8.5)
		line3 = ROOT.TLine(100,2.5,150,2.5)
		line4 = ROOT.TLine(150,1.5,150,2.5)
		line1.SetLineColor(ROOT.kBlue+2)
		line2.SetLineColor(ROOT.kBlue+2)
		line3.SetLineColor(ROOT.kBlue+2)
		line4.SetLineColor(ROOT.kBlue+2)

		line1.SetLineWidth(4)
		line2.SetLineWidth(4)
		line3.SetLineWidth(4)
		line4.SetLineWidth(4)
		line1.SetLineStyle(2)
		line2.SetLineStyle(2)
		line3.SetLineStyle(2)
		line4.SetLineStyle(2)
		
		line5 = ROOT.TLine(100,1.5,150,1.5)
		line6 = ROOT.TLine(100,1.5,100,2.5)
		line7 = ROOT.TLine(100,2.5,150,2.5)
		line8 = ROOT.TLine(150,1.5,150,2.5)
		#~ line5.SetLineColor(ROOT.kRed)
		#~ line6.SetLineColor(ROOT.kRed)
		#~ line7.SetLineColor(ROOT.kRed)
		#~ line8.SetLineColor(ROOT.kRed)

		line5.SetLineWidth(4)
		line6.SetLineWidth(4)
		line7.SetLineWidth(4)
		line8.SetLineWidth(4)
		#~ line5.SetLineStyle(2)
		#~ line6.SetLineStyle(2)
		#~ line7.SetLineStyle(2)
		#~ line8.SetLineStyle(2)
		
		line9 = ROOT.TLine(0,1.5,50,1.5)
		line10 = ROOT.TLine(0,1.5,0,8.5)
		line11 = ROOT.TLine(0,2.5,50,2.5)
		line12 = ROOT.TLine(50,1.5,50,8.5)
		#~ line9.SetLineColor(ROOT.kRed)
		#~ line1.SetLineColor(ROOT.kRed)
		#~ line7.SetLineColor(ROOT.kRed)
		#~ line8.SetLineColor(ROOT.kRed)

		line9.SetLineWidth(4)
		line10.SetLineWidth(4)
		line11.SetLineWidth(4)
		line12.SetLineWidth(4)
		line9.SetLineStyle(3)
		line10.SetLineStyle(3)
		line11.SetLineStyle(3)
		line12.SetLineStyle(3)
	#~ 
		line5.Draw("same")
		line6.Draw("same")
		line7.Draw("same")
		line8.Draw("same")
		line1.Draw("same")
		line2.Draw("same")
		line3.Draw("same")
		line4.Draw("same")
		line9.Draw("same")
		line10.Draw("same")
		#~ line11.Draw("same")
		line12.Draw("same")

		legend.AddEntry(line1,"signal region","l")
		legend.AddEntry(line5,"FS control region","l")
		legend.AddEntry(line9,"DY control region","l")
		legend.Draw("same")
		
		latex = ROOT.TLatex()
		latex.SetTextFont(42)
		latex.SetTextAlign(31)
		latex.SetTextSize(0.04)
		latex.SetNDC(True)
		latexCMS = ROOT.TLatex()
		latexCMS.SetTextFont(61)
		latexCMS.SetTextSize(0.06)
		latexCMS.SetNDC(True)
		latexCMSExtra = ROOT.TLatex()
		latexCMSExtra.SetTextFont(52)
		latexCMSExtra.SetTextSize(0.045)
		latexCMSExtra.SetNDC(True)
		#~ 
		
		cmsExtra = "#splitline{Private Work}{Simulation}"
		
		latex.DrawLatex(0.9, 0.96, "%s fb^{-1} (8 TeV)"%19.5)
		

		latexCMS.DrawLatex(0.19,0.88,"CMS")
		if "Simulation" in cmsExtra:
			yLabelPos = 0.81	
		else:
			yLabelPos = 0.84	

		latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))	
	
		
		latexCentral = ROOT.TLatex()
		latexCentral.SetTextFont(42)
		latexCentral.SetTextAlign(31)
		latexCentral.SetTextSize(0.07)
		latexCentral.SetNDC(True)	
		#~ latexCentral.DrawLatex(0.4,0.45,"Central")
		latexForward = ROOT.TLatex()
		latexForward.SetTextFont(42)
		latexForward.SetTextAlign(31)
		latexForward.SetTextSize(0.07)
		latexForward.SetNDC(True)	
		#~ latexForward.DrawLatex(0.88,0.45,"Forward")
		

		hCanvas.Print("metJetsScatter_%s.pdf"%fileNames[SampleName])
