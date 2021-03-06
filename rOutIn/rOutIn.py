#!/usr/bin/env python

import sys
sys.path.append('cfg/')
from frameworkStructure import pathes
sys.path.append(pathes.basePath)

import os
import pickle

from messageLogger import messageLogger as log

import math
from math import sqrt
from array import array

import argparse	


import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
ROOT.gROOT.SetBatch(True)
from ROOT import TCanvas, TEfficiency, TPad, TH1F, TH1I, THStack, TLegend, TMath, TGraphAsymmErrors, TF1, gStyle


from defs import getRegion, getPlot, getRunRange, Backgrounds

from setTDRStyle import setTDRStyle
from helpers import readTrees, getDataHist, TheStack, totalNumberOfGeneratedEvents, Process

from corrections import rSFOF, rEEOF, rMMOF
from centralConfig import regionsToUse, runRanges, backgroundLists, plotLists, systematics, mllBins
import corrections



from locations import locations


def getHistograms(path,plot,runRange,isMC,backgrounds):

	treesEE = readTrees(path,"EE")
	treesEM = readTrees(path,"EMu")
	treesMM = readTrees(path,"MuMu")
		
	
	
	if isMC:
		
		eventCounts = totalNumberOfGeneratedEvents(path)	
		processes = []
		for background in backgrounds:
			processes.append(Process(getattr(Backgrounds,background),eventCounts))
		histoEE = TheStack(processes,runRange.lumi,plot,treesEE,"None",1.0,1.0,1.0).theHistogram		
		histoMM = TheStack(processes,runRange.lumi,plot,treesMM,"None",1.0,1.0,1.0).theHistogram
		histoEM = TheStack(processes,runRange.lumi,plot,treesEM,"None",1.0,1.0,1.0).theHistogram
		#~ histoEE.Scale(getattr(triggerEffs,region).effEE.val)
		#~ histoMM.Scale(getattr(triggerEffs,region).effMM.val)	
		#~ histoEM.Scale(getattr(triggerEffs,region).effEM.val)				
		
	else:
		histoEE = getDataHist(plot,treesEE)
		histoMM = getDataHist(plot,treesMM)
		histoEM = getDataHist(plot,treesEM)
	
	return histoEE , histoMM, histoEM


	
def plotMllSpectra(SFhist,EMuhist,runRange,selection,suffix,cmsExtra,additionalLabel):

		
	SFhist.Rebin(5)
	EMuhist.Rebin(5)

	hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
	plotPad = TPad("plotPad","plotPad",0,0,1,1)
	
	style=setTDRStyle()
	style.SetTitleYOffset(1.6)
	style.SetPadLeftMargin(0.19)		
	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()				
	

	
	plotPad.DrawFrame(20,0,300,SFhist.GetBinContent(SFhist.GetMaximumBin())*1.5,"; %s ; %s" %("m_{ll} [GeV]","Events / 5 GeV"))		

	
	SFhist.SetMarkerStyle(20)
	SFhist.SetMarkerColor(ROOT.kBlack)
	
	EMuhist.Draw("samehist")
	SFhist.Draw("samepe")
	EMuhist.SetFillColor(855)
	legend = TLegend(0.6, 0.7, 0.95, 0.95)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)
	ROOT.gStyle.SetOptStat(0)	
	legend.AddEntry(SFhist,"%s events"%suffix,"p")
	legend.AddEntry(EMuhist,"OF events","f")
	legend.Draw("same")

	
	line1 = ROOT.TLine(mllBins.lowMass.low,0,mllBins.lowMass.low,SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line2 = ROOT.TLine(mllBins.lowMass.high,0,mllBins.lowMass.high,SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line3 = ROOT.TLine(mllBins.onZ.low,0,mllBins.onZ.low,SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line4 = ROOT.TLine(mllBins.onZ.high,0,mllBins.onZ.high,SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line5 = ROOT.TLine(mllBins.highMass.low,0,mllBins.highMass.low,SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line1.SetLineColor(ROOT.kBlack)
	line2.SetLineColor(ROOT.kBlack)
	line3.SetLineColor(ROOT.kRed+2)
	line4.SetLineColor(ROOT.kRed+2)
	line5.SetLineColor(ROOT.kBlack)
	line1.SetLineWidth(2)
	line2.SetLineWidth(2)
	line3.SetLineWidth(2)
	line4.SetLineWidth(2)
	line5.SetLineWidth(2)
	line1.Draw("same")
	line2.Draw("same")
	line3.Draw("same")
	line4.Draw("same")
	line5.Draw("same")

	Labelin = ROOT.TLatex()
	Labelin.SetTextAlign(12)
	Labelin.SetTextSize(0.04)
	Labelin.SetTextColor(ROOT.kRed+2)
	Labelout = ROOT.TLatex()
	Labelout.SetTextAlign(12)
	Labelout.SetTextSize(0.04)
	Labelout.SetTextColor(ROOT.kBlack)	
	
	
	Labelin.DrawLatex(80.75,SFhist.GetBinContent(SFhist.GetMaximumBin())/1.5,"In")
	Labelout.DrawLatex(27.25,SFhist.GetBinContent(SFhist.GetMaximumBin())/1.5,"Out")
	Labelout.DrawLatex(150.25,SFhist.GetBinContent(SFhist.GetMaximumBin())/1.5,"Out")	
	
	latex = ROOT.TLatex()
	latex.SetTextFont(42)
	latex.SetTextAlign(31)
	latex.SetTextSize(0.04)
	latex.SetNDC(True)
	latexCMS = ROOT.TLatex()
	latexCMS.SetTextFont(61)
	latexCMS.SetTextSize(0.055)
	latexCMS.SetNDC(True)
	latexCMSExtra = ROOT.TLatex()
	latexCMSExtra.SetTextFont(52)
	latexCMSExtra.SetTextSize(0.03)
	latexCMSExtra.SetNDC(True) 
		
	latex.DrawLatex(0.95, 0.96, "%s fb^{-1} (13 TeV)"%runRange.printval)
	

	latexCMS.DrawLatex(0.21,0.88,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.81	
	else:
		yLabelPos = 0.84	

	latexCMSExtra.DrawLatex(0.21,yLabelPos,"%s"%(cmsExtra))
	
	plotPad.RedrawAxis()
	if additionalLabel is not "":
		hCanvas.Print("fig/rOutIn_NoLog_%s_%s_%s_%s.pdf"%(selection.name,suffix,runRange.label,additionalLabel))
	else:
		hCanvas.Print("fig/rOutIn_NoLog_%s_%s_%s.pdf"%(selection.name,suffix,runRange.label))
			
	
	
	
	hCanvas.Clear()
	
	plotPad = TPad("plotPad","plotPad",0,0,1,1)
	
	style=setTDRStyle()
	plotPad.UseCurrentStyle()
	plotPad.Draw()	
	plotPad.cd()				
	

	
	plotPad.DrawFrame(mllBins.lowMass.low,1,300,SFhist.GetBinContent(SFhist.GetMaximumBin())*10,"; %s ; %s" %("m_{ll} [GeV]","Events / 5 GeV"))		
	
	plotPad.SetLogy()

	
	EMuhist.Draw("samehist")
	SFhist.Draw("samepe")
	legend.Draw("same")
	

	line1.SetY2(SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line2.SetY2(SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line3.SetY2(SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line4.SetY2(SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line5.SetY2(SFhist.GetBinContent(SFhist.GetMaximumBin()))
	line1.Draw("same")
	line2.Draw("same")
	line3.Draw("same")
	line4.Draw("same")
	line5.Draw("same")
	Labelin.SetTextAngle(90)
	Labelin.DrawLatex(89.35,SFhist.GetBinContent(SFhist.GetMaximumBin())/18,"on Z")
	Labelout.SetTextAngle(90)
	Labelout.DrawLatex(47.25,SFhist.GetBinContent(SFhist.GetMaximumBin())/18,"low mass")
	#~ Labelout.DrawLatex(75.25,SFhist.GetBinContent(SFhist.GetMaximumBin())/18,"below Z")
	#~ Labelout.DrawLatex(109.25,SFhist.GetBinContent(SFhist.GetMaximumBin())/18,"above Z")
	Labelout.DrawLatex(150.25,SFhist.GetBinContent(SFhist.GetMaximumBin())/18,"high mass")
	latex.DrawLatex(0.95, 0.96, "%s fb^{-1} (13 TeV)"%runRange.printval)
	

	latexCMS.DrawLatex(0.19,0.88,"CMS")
	if "Simulation" in cmsExtra:
		yLabelPos = 0.825	
	else:
		yLabelPos = 0.84	

	latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra)) 	
	plotPad.RedrawAxis()
	if additionalLabel is not "":
		hCanvas.Print("fig/rOutIn_%s_%s_%s_%s.pdf"%(suffix,selection.name,runRange.label,additionalLabel))	
	else:
		hCanvas.Print("fig/rOutIn_%s_%s_%s.pdf"%(suffix,selection.name,runRange.label))	
	
	
def dependencies(path,selection,plots,runRange,mc,backgrounds,cmsExtra):
	hCanvas = TCanvas("hCanvas", "Distribution", 800,800)
	legend = TLegend(0.6, 0.7, 0.9, 0.9)
	legend.SetFillStyle(0)
	legend.SetBorderSize(0)
	ROOT.gStyle.SetOptStat(0)		
	
	for name in plots:
		hCanvas.Clear()
		
		plot = getPlot(name)
		plot.addRegion(selection)
		plot.cleanCuts()	
		plot.cuts = plot.cuts % runRange.runCut	

		if not "Forward" in selection.name:
			relSyst = systematics.rOutIn.central.val
			if "Central" in selection.name:
				region = "central"
			else:
				region = "inclusive"
		else:	
			relSyst = systematics.rOutIn.forward.val
			region = "forward"	
		 
		if len(plot.binning) == 0:
			bins = [plot.firstBin+(plot.lastBin-plot.firstBin)/plot.nBins*i for i in range(plot.nBins+1)]
		else:
			bins = plot.binning
		#~ rOutIn = {"LowMass":{"EE":[],"MM":[],"SF":[]},"HighMass":{"EE":[],"MM":[],"SF":[]},"BelowZ":{"EE":[],"MM":[],"SF":[]},"AboveZ":{"EE":[],"MM":[],"SF":[]}}
		#~ rOutInErr = {"LowMass":{"EE":[],"MM":[],"SF":[]},"HighMass":{"EE":[],"MM":[],"SF":[]},"BelowZ":{"EE":[],"MM":[],"SF":[]},"AboveZ":{"EE":[],"MM":[],"SF":[]}}
		rOutIn = {"EdgeMass":{"EE":[],"MM":[],"SF":[]},"LowMass":{"EE":[],"MM":[],"SF":[]},"HighMass":{"EE":[],"MM":[],"SF":[]},}
		rOutInErr = {"EdgeMass":{"EE":[],"MM":[],"SF":[]},"LowMass":{"EE":[],"MM":[],"SF":[]},"HighMass":{"EE":[],"MM":[],"SF":[]}}


		binningErrs	= []
		plotBinning = []
		for i in range(0,len(bins)-1):
			binningErrs.append((bins[i+1]-bins[i])/2)
			if i == 0:
				plotBinning.append((bins[i+1]-abs(bins[i]))/2)
			else:
				plotBinning.append(plotBinning[i-1]+(bins[i+1]-bins[i])/2+binningErrs[i-1])

			tmpCuts = selection.cut 
			cuts = selection.cut.split("&&")
			cutsUp = [] 
			cutsDown = [] 
			cutsEqual = []
			for cut in cuts:
				if "%s >"%plot.variable in cut:
					cutsUp.append(cut+ "&&")
				elif "%s <"%plot.variable in cut:
					cutsDown.append(cut+ "&&")
				elif "%s =="%plot.variable in cut:
					cutsEqual.append(cut+ "&&")
			for cut in cutsUp:
				selection.cut = selection.cut.replace(cut,"")		
			for cut in cutsDown:
				selection.cut = selection.cut.replace(cut,"")		
			for cut in cutsEqual:
				selection.cut = selection.cut.replace(cut,"")		
			selection.cut = selection.cut + " && %s > %f && %s < %f"%(plot.variable,bins[i],plot.variable,bins[i+1]) + " && %s"%runRange.runCut
				
			additionalLabel = "%s_%.2f_%.2f"%(plot.variable,bins[i],bins[i+1])
			centralVal = centralValues(path,selection,runRange,mc,backgrounds,cmsExtra,additionalLabel)
			for combination in ["EE","MM","SF"]:
				#~ for region in ["LowMass","HighMass","BelowZ","AboveZ"]:
				for region in ["EdgeMass","LowMass","HighMass"]:
					rOutIn[region][combination].append(centralVal["rOutIn%s%s"%(region,combination)])
					rOutInErr[region][combination].append(centralVal["rOutIn%sErr%s"%(region,combination)])


			
			selection.cut = tmpCuts
		if mc:		
			if os.path.isfile("shelves/rOutIn_%s_%s_MC.pkl"%(selection.name,runRange.label)):
				centralVals = pickle.load(open("shelves/rOutIn_%s_%s_MC.pkl"%(selection.name,runRange.label),"rb"))
			else:
				centralVals = centralValues(path,selection,runRange,mc,backgrounds,cmsExtra)					
		else:
			if os.path.isfile("shelves/rOutIn_%s_%s.pkl"%(selection.name,runRange.label)):
				centralVals = pickle.load(open("shelves/rOutIn_%s_%s.pkl"%(selection.name,runRange.label),"rb"))
			else:
				centralVals = centralValues(path,selection,runRange,mc,backgrounds,cmsExtra)		
		
		for combination in ["EE","MM","SF"]:
			relSystSave = relSyst
			#~ for region in ["LowMass","HighMass","BelowZ","AboveZ"]:
			for region in ["EdgeMass","LowMass","HighMass"]:
				relSyst = relSystSave	
				hCanvas = TCanvas("hCanvas", "Distribution", 800,800)

				plotPad = TPad("plotPad","plotPad",0,0,1,1)
				
				style=setTDRStyle()
				style.SetTitleYOffset(1.3)
				style.SetPadLeftMargin(0.16)		
				plotPad.UseCurrentStyle()
				plotPad.Draw()	
				plotPad.cd()
		
				plotPad.DrawFrame(plot.firstBin,0.0,plot.lastBin,0.15,"; %s ; %s" %(plot.xaxis,"R_{out/in}"))		
				
				
				bandX = array("f",[plot.firstBin,plot.lastBin])
				bandY = array("f",[centralVals["rOutIn%s%s"%(region,combination)],centralVals["rOutIn%s%s"%(region,combination)]])
				bandYErr = array("f",[centralVals["rOutIn%s%s"%(region,combination)]*relSyst,centralVals["rOutIn%s%s"%(region,combination)]*relSyst])
				bandXErr = array("f",[0,0])
				
				
				errorband = ROOT.TGraphErrors(2,bandX,bandY,bandXErr,bandYErr)
				errorband.GetYaxis().SetRangeUser(0.0,0.15)
				errorband.GetXaxis().SetRangeUser(-5,105)
				errorband.Draw("3same")
				errorband.SetFillColor(ROOT.kOrange-9)
				rOutInLine = ROOT.TLine(plot.firstBin,centralVals["rOutIn%s%s"%(region,combination)],plot.lastBin,centralVals["rOutIn%s%s"%(region,combination)])
				rOutInLine.SetLineStyle(ROOT.kDashed)
				rOutInLine.SetLineWidth(2)
				rOutInLine.Draw("same")

				
				
				
				binning = array("f",plotBinning)
				rOutInVals = array("f",rOutIn[region][combination])
				binningErrs = array("f",binningErrs)
				rOutInValsErrs = array("f",rOutInErr[region][combination])	
				graph = ROOT.TGraphErrors(len(binning),binning,rOutInVals,binningErrs,rOutInValsErrs)
				graph.Draw("Psame0")
				legend.Clear()

				if mc:
					legend.AddEntry(graph,"r_{out,in} MC","p")
				else:
					legend.AddEntry(graph,"r_{out,in} Data","p")
				legend.AddEntry(rOutInLine, "Mean r_{out,in} = %.3f"%centralVals["rOutIn%s%s"%(region,combination)],"l")
				legend.AddEntry(errorband, "Mean r_{out,in} #pm %d %%"%(relSyst*100),"f")
				legend.Draw("same")


				latex = ROOT.TLatex()
				latex.SetTextFont(42)
				latex.SetTextAlign(31)
				latex.SetTextSize(0.04)
				latex.SetNDC(True)
				latexCMS = ROOT.TLatex()
				latexCMS.SetTextFont(61)
				latexCMS.SetTextSize(0.055)
				latexCMS.SetNDC(True)
				latexCMSExtra = ROOT.TLatex()
				latexCMSExtra.SetTextFont(52)
				latexCMSExtra.SetTextSize(0.03)
				latexCMSExtra.SetNDC(True) 
					
				latex.DrawLatex(0.95, 0.96, "%s fb^{-1} (13 TeV)"%runRange.printval)
				

				latexCMS.DrawLatex(0.19,0.89,"CMS")
				if "Simulation" in cmsExtra:
					yLabelPos = 0.83	
				else:
					yLabelPos = 0.85	

				latexCMSExtra.DrawLatex(0.19,yLabelPos,"%s"%(cmsExtra))		
					
				ROOT.gPad.RedrawAxis()
				if mc:
					hCanvas.Print("fig/rOutInSyst_%s_%s_%s_%s_%s_%s_MC.pdf"%(selection.name,runRange.label,plot.variablePlotName,region,combination,plot.additionalName))
				else:
					hCanvas.Print("fig/rOutInSyst_%s_%s_%s_%s_%s_%s.pdf"%(selection.name,runRange.label,plot.variablePlotName,region,combination,plot.additionalName))

	
	

	
	
def centralValues(path,selection,runRange,isMC,backgrounds,cmsExtra,additionalLabel=""):			
			

	plot = getPlot("mllPlotROutIn")
	plot.addRegion(selection)
	plot.cleanCuts()
	plot.cuts = plot.cuts % runRange.runCut		

	
	if not "Forward" in selection.name:
		region = "central"
	else:		
		region = "forward"

	histEE, histMM, histEM = getHistograms(path,plot,runRange,isMC,backgrounds)
	histSF = histEE.Clone("histSF")
	histSF.Add(histMM.Clone())

	result = {}
	edgeMassLow = mllBins.edgeMass.low
	edgeMassHigh = mllBins.edgeMass.high
	lowMassLow = mllBins.lowMass.low
	lowMassHigh = mllBins.lowMass.high
	peakLow = mllBins.onZ.low
	peakHigh = mllBins.onZ.high
	highMassLow = mllBins.highMass.low
	highMassHigh = mllBins.highMass.high
	#~ belowZLow = mllBins.belowZ.low
	#~ belowZHigh = mllBins.belowZ.high
	#~ aboveZLow = mllBins.aboveZ.low
	#~ aboveZHigh = mllBins.aboveZ.high

		
	result["peakEE"] = histEE.Integral(histEE.FindBin(peakLow+0.01),histEE.FindBin(peakHigh-0.01))
	result["peakMM"] = histMM.Integral(histMM.FindBin(peakLow+0.01),histMM.FindBin(peakHigh-0.01))
	result["peakSF"] = result["peakEE"] + result["peakMM"]
	result["peakOF"] = histEM.Integral(histEM.FindBin(peakLow+0.01),histEM.FindBin(peakHigh-0.01))

	result["edgeMassEE"] = histEE.Integral(histEE.FindBin(edgeMassLow+0.01),histEE.FindBin(edgeMassHigh-0.01))
	result["edgeMassMM"] = histMM.Integral(histMM.FindBin(edgeMassLow+0.01),histMM.FindBin(edgeMassHigh-0.01))
	result["edgeMassSF"] = result["edgeMassEE"] + result["edgeMassMM"]
	result["edgeMassOF"] = histEM.Integral(histEM.FindBin(edgeMassLow),histEM.FindBin(edgeMassHigh-0.01))
	result["lowMassEE"] = histEE.Integral(histEE.FindBin(lowMassLow+0.01),histEE.FindBin(lowMassHigh-0.01))
	result["lowMassMM"] = histMM.Integral(histMM.FindBin(lowMassLow+0.01),histMM.FindBin(lowMassHigh-0.01))
	result["lowMassSF"] = result["lowMassEE"] + result["lowMassMM"]
	result["lowMassOF"] = histEM.Integral(histEM.FindBin(lowMassLow),histEM.FindBin(lowMassHigh-0.01))
	result["highMassEE"] = histEE.Integral(histEE.FindBin(highMassLow+0.01),histEE.FindBin(highMassHigh))
	result["highMassMM"] = histMM.Integral(histMM.FindBin(highMassLow+0.01),histMM.FindBin(highMassHigh))
	result["highMassSF"] = result["highMassEE"] + result["highMassMM"]
	result["highMassOF"] = histEM.Integral(histEM.FindBin(highMassLow+0.01),histEM.FindBin(highMassHigh))
	
	#~ result["belowZEE"] = histEE.Integral(histEE.FindBin(belowZLow+0.01),histEE.FindBin(belowZHigh-0.01))
	#~ result["belowZMM"] = histMM.Integral(histMM.FindBin(belowZLow+0.01),histMM.FindBin(belowZHigh-0.01))
	#~ result["belowZSF"] = result["belowZEE"] + result["belowZMM"]
	#~ result["belowZOF"] = histEM.Integral(histEM.FindBin(belowZLow),histEM.FindBin(belowZHigh-0.01))
	#~ result["aboveZEE"] = histEE.Integral(histEE.FindBin(aboveZLow+0.01),histEE.FindBin(aboveZHigh))
	#~ result["aboveZMM"] = histMM.Integral(histMM.FindBin(aboveZLow+0.01),histMM.FindBin(aboveZHigh))
	#~ result["aboveZSF"] = result["aboveZEE"] + result["aboveZMM"]
	#~ result["aboveZOF"] = histEM.Integral(histEM.FindBin(aboveZLow+0.01),histEM.FindBin(aboveZHigh))

	for combination in ["EE","MM","SF"]:
		corr = getattr(corrections,"r%sOF"%combination).central.val
		corrErr = getattr(corrections,"r%sOF"%combination).central.err
		if isMC:
			corr = getattr(corrections,"r%sOF"%combination).central.valMC
			corrErr = getattr(corrections,"r%sOF"%combination).central.errMC
		peak = result["peak%s"%combination] - result["peakOF"]*corr			
		peakErr = sqrt(result["peak%s"%combination] + (sqrt(result["peakOF"])*corr)**2 + (sqrt(result["peakOF"])*corr*corrErr)**2)

		lowMass = result["lowMass%s"%combination] - result["lowMassOF"]*corr			
		lowMassErr = sqrt(result["lowMass%s"%combination] + (sqrt(result["lowMassOF"])*corr)**2 + (sqrt(result["lowMassOF"])*corr*corrErr)**2)
		edgeMass = result["edgeMass%s"%combination] - result["edgeMassOF"]*corr			
		edgeMassErr = sqrt(result["edgeMass%s"%combination] + (sqrt(result["edgeMassOF"])*corr)**2 + (sqrt(result["edgeMassOF"])*corr*corrErr)**2)
		highMass = result["highMass%s"%combination] - result["highMassOF"]*corr			
		highMassErr = sqrt(result["highMass%s"%combination] + (sqrt(result["highMassOF"])*corr)**2 + (sqrt(result["highMassOF"])*corr*corrErr)**2)	
				
		#~ belowZ = result["belowZ%s"%combination] - result["belowZOF"]*corr			
		#~ belowZErr = sqrt(result["belowZ%s"%combination] + (sqrt(result["belowZOF"])*corr)**2 + (sqrt(result["belowZOF"])*corr*corrErr)**2)
		#~ aboveZ = result["aboveZ%s"%combination] - result["aboveZOF"]*corr			
		#~ aboveZErr = sqrt(result["aboveZ%s"%combination] + (sqrt(result["aboveZOF"])*corr)**2 + (sqrt(result["aboveZOF"])*corr*corrErr)**2)	
				
		result["correctedPeak%s"%combination] = peak
		result["peakError%s"%combination] = peakErr

		result["correctedEdgeMass%s"%combination] = edgeMass
		result["edgeMassError%s"%combination] = edgeMassErr
		result["correctedLowMass%s"%combination] = lowMass
		result["lowMassError%s"%combination] = lowMassErr
		result["correctedHighMass%s"%combination] = highMass
		result["highMassError%s"%combination] = highMassErr

		#~ result["correctedBelowZ%s"%combination] = belowZ
		#~ result["belowZError%s"%combination] = belowZErr
		#~ result["correctedAboveZ%s"%combination] = aboveZ
		#~ result["aboveZError%s"%combination] = aboveZErr
		
		result["correction"] = 	corr
		result["correctionErr"] = 	corrErr
	
		rOutInEdgeMass =   edgeMass / peak
		rOutInLowMass =   lowMass / peak
		rOutInHighMass = highMass / peak
		rOutInEdgeMassSystErr = rOutInEdgeMass*systematics.rOutIn.central.val
		rOutInLowMassSystErr = rOutInLowMass*systematics.rOutIn.central.val
		rOutInHighMassSystErr = rOutInHighMass*systematics.rOutIn.central.val
		rOutInEdgeMassErr = sqrt((edgeMassErr/peak)**2 + (edgeMass*peakErr/peak**2)**2)
		rOutInLowMassErr = sqrt((lowMassErr/peak)**2 + (lowMass*peakErr/peak**2)**2)
		rOutInHighMassErr = sqrt((highMassErr/peak)**2 + (highMass*peakErr/peak**2)**2)
	
		#~ rOutInBelowZ =   belowZ / peak
		#~ rOutInAboveZ = aboveZ / peak
		#~ rOutInBelowZSystErr = rOutInBelowZ*systematics.rOutIn.central.val
		#~ rOutInAboveZSystErr = rOutInAboveZ*systematics.rOutIn.central.val
		#~ rOutInBelowZErr = sqrt((belowZErr/peak)**2 + (belowZ*peakErr/peak**2)**2)
		#~ rOutInAboveZErr = sqrt((aboveZErr/peak)**2 + (aboveZ*peakErr/peak**2)**2)


		result["rOutInEdgeMass%s"%combination] = rOutInEdgeMass
		result["rOutInEdgeMassErr%s"%combination] = rOutInEdgeMassErr
		result["rOutInEdgeMassSyst%s"%combination] = rOutInEdgeMassSystErr
		result["rOutInLowMass%s"%combination] = rOutInLowMass
		result["rOutInLowMassErr%s"%combination] = rOutInLowMassErr
		result["rOutInLowMassSyst%s"%combination] = rOutInLowMassSystErr
		result["rOutInHighMass%s"%combination] = rOutInHighMass
		result["rOutInHighMassErr%s"%combination] = rOutInHighMassErr
		result["rOutInHighMassSyst%s"%combination] = rOutInHighMassSystErr

		#~ result["rOutInBelowZ%s"%combination] = rOutInBelowZ
		#~ result["rOutInBelowZErr%s"%combination] = rOutInBelowZErr
		#~ result["rOutInBelowZSyst%s"%combination] = rOutInBelowZSystErr
		#~ result["rOutInAboveZ%s"%combination] = rOutInAboveZ
		#~ result["rOutInAboveZErr%s"%combination] = rOutInAboveZErr
		#~ result["rOutInAboveZSyst%s"%combination] = rOutInAboveZSystErr

		
		saveLabel = additionalLabel
		tmpLabel = additionalLabel
		if isMC:
			tmpLabel += "_MC"

		histEMToPlot = histEM.Clone()
		histEMToPlot.Scale(corr)
		additionalLabel = tmpLabel
		if combination == "EE":
			plotMllSpectra(histEE.Clone(),histEMToPlot,runRange,selection,combination,cmsExtra,additionalLabel)
		elif combination == "MM":	
			plotMllSpectra(histMM.Clone(),histEMToPlot,runRange,selection,combination,cmsExtra,additionalLabel)
		else:	
			plotMllSpectra(histSF.Clone(),histEMToPlot,runRange,selection,combination,cmsExtra,additionalLabel)
			

		additionalLabel = saveLabel
		




	return result
def main():



	parser = argparse.ArgumentParser(description='R(out/in) measurements.')
	
	parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False,
						  help="Verbose mode.")
	parser.add_argument("-m", "--mc", action="store_true", dest="mc", default=False,
						  help="use MC, default is to use data.")
	parser.add_argument("-s", "--selection", dest = "selection" , action="append", default=[],
						  help="selection which to apply.")
	parser.add_argument("-p", "--plot", dest="plots", action="append", default=[],
						  help="select dependencies to study, default is all.")
	parser.add_argument("-r", "--runRange", dest="runRange", action="append", default=[],
						  help="name of run range.")
	parser.add_argument("-c", "--centralValues", action="store_true", dest="central", default=False,
						  help="calculate R(out/in) central values")
	parser.add_argument("-b", "--backgrounds", dest="backgrounds", action="append", default=[],
						  help="backgrounds to plot.")
	parser.add_argument("-d", "--dependencies", action="store_true", dest="dependencies", default= False,
						  help="make dependency plots")		
	parser.add_argument("-x", "--private", action="store_true", dest="private", default=False,
						  help="plot is private work.")	
	parser.add_argument("-w", "--write", action="store_true", dest="write", default=False,
						  help="write results to central repository")	
					
	args = parser.parse_args()



	if len(args.backgrounds) == 0:
		args.backgrounds = backgroundLists.default
	if len(args.plots) == 0:
		args.plots = plotLists.rOutIn
	if len(args.selection) == 0:
		args.selection.append(regionsToUse.rOutIn.central.name)	
		args.selection.append(regionsToUse.rOutIn.forward.name)	
		args.selection.append(regionsToUse.rOutIn.inclusive.name)	
	if len(args.runRange) == 0:
		args.runRange.append(runRanges.name)	


	path = locations.dataSetPath


	cmsExtra = ""
	if args.private:
		cmsExtra = "Private Work"
		if args.mc:
			cmsExtra = "#splitline{Private Work}{Simulation}"
	elif args.mc:
		cmsExtra = "Simulation"	
	else:
		cmsExtra = "Preliminary"

	for runRangeName in args.runRange:
		runRange = getRunRange(runRangeName)
	
		for selectionName in args.selection:
			
			selection = getRegion(selectionName)


			if args.central:
				centralVal = centralValues(path,selection,runRange,args.mc,args.backgrounds,cmsExtra)
				if args.mc:
					outFilePkl = open("shelves/rOutIn_%s_%s_MC.pkl"%(selection.name,runRange.label),"w")
				else:
					outFilePkl = open("shelves/rOutIn_%s_%s.pkl"%(selection.name,runRange.label),"w")
				pickle.dump(centralVal, outFilePkl)
				outFilePkl.close()
				
			if args.dependencies:
				 dependencies(path,selection,args.plots,runRange,args.mc,args.backgrounds,cmsExtra)	
				 
			if args.write:
				import subprocess
				if args.mc:
					bashCommand = "cp shelves/rOutIn_%s_%s_MC.pkl %s/shelves"%(selection.name,runRange.label,pathes.basePath)		
				else:	
					bashCommand = "cp shelves/rOutIn_%s_%s.pkl %s/shelves"%(selection.name,runRange.label,pathes.basePath)
				process = subprocess.Popen(bashCommand.split())				 					 	
	

main()
