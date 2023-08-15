# -*- coding: utf-8 -*-

"""
/***************************************************************************
 ICEDCamelPlot
                                 A QGIS plugin
 This plugin creates camelplots for each site based on multiple exposure ages and links the camelplots to each site
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2023-08-05
        copyright            : (C) 2023 by Yingkui Li
        email                : yli32@utk.edu
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'Yingkui Li'
__date__ = '2023-08-05'
__copyright__ = '(C) 2023 by Yingkui Li'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import matplotlib
matplotlib.use('agg')

import matplotlib.pyplot as plt
import numpy as np

import os
import inspect
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtCore import *

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsPoint,
                       QgsProject,
                       QgsGeometry,
                       QgsField,
                       QgsFields,
                       QgsWkbTypes,
                       #QVariant,
                       QgsFeature,
                       QgsVectorLayer,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterFolderDestination,
                       QgsProcessingParameterFileDestination) ##for a file

#----------------------------------------------------------------------------------------
#This function creates a camelplot based on multiple exposure ages and internal errors.
#This function is revised based on the codes from Madeline Waldock
#----------------------------------------------------------------------------------------
def camelplot(ages, errors, names, site_name, ax):##, outfolder): ##, summary_std1, skewness, summary_variance, chisq):
    numsamples = len(ages)
    sortindex = np.argsort(ages)
    min_index = sortindex[0]
    max_index = sortindex[-1]
    minAge = ages[min_index] - 4 * errors[min_index]
    maxAge = ages[max_index] + 4 * errors[max_index]
    
    x = np.linspace(minAge, maxAge, 1000)
    totalPdf = np.zeros_like(x)  # initialize array to store summary PDF

    pdfs = np.zeros((numsamples, len(x)))  # initialize array to store PDFs

    ax.set_title(f'Camelplot for Site {site_name}')
    ax.set_xlabel('Age (ka)')
    ax.set_ylabel('Probability Density (%)')
    ax.set_xlim([minAge, maxAge])

    handles, labels = [], []

    # Calculate the mean and standard deviation for each summary curve
    means = np.zeros(numsamples)
    stds = np.zeros(numsamples)

    for a in range(numsamples):
        mu = ages[a]
        sigma = errors[a]
        xn = (x - mu) / sigma
        y = np.exp(-0.5 * xn ** 2) / (np.sqrt(2 * np.pi) * sigma)
        pdfs[a] = y  # store PDF for current sample
        totalPdf += y / numsamples  # update summary PDF

        # Calculate the mean and standard deviation for the current summary curve
        means[a] = mu
        stds[a] = sigma

        # Add the current PDF to the plot and update the legend
        label = f'{names[a]} ({mu:.2f}+-{sigma:.2f})' # include age, error, and skew value in label
        h = ax.plot(x, y*100 / numsamples, alpha=0.5, label=label)
        handles.append(h[0])
        labels.append(label)

    # Calculate the mean, median, variance and standard deviation of the samples within the site
    summary_mean = (np.sum(means))/numsamples
    summary_std = np.sqrt(np.sum(stds ** 2) / numsamples)
    #summary_median = np.median(means)
    if numsamples > 2:
        summary_std1 = np.std(means, ddof=1)
        summary_variance = np.var(means, ddof=1)
    else:
        summary_std1 = np.std(means)
        summary_variance = np.var(means)

    # Calculate skewness for the current site
    skewness = 0.0
    for a in range(numsamples):
        if numsamples > 2:
            xn = (ages[a] - summary_mean)**3/ (summary_std1**3)
            skewness += (xn)
    if numsamples > 2:
        skewness *= (numsamples / ((numsamples - 1) * (numsamples - 2)))
    else:
        skewness = 0.0
    
    # Calculate chi-squared value
    chisq = 0.0
    chisq = np.sum((means-summary_mean)**2 / stds**2)
    if numsamples >2:
        chisq /= ((numsamples - 1))
    else:
        chisq = 0
 
    label = f'Summary Curve (Mean:{summary_mean:.2f}, Error:{summary_std:.2f})\nSample Std:{summary_std1:.2f}, Skew:{skewness:.2f}, Chi-sq:{chisq:.2f}'
    ax.plot(x, totalPdf*100, 'k', label=label)
    handles.append(ax.lines[-1])
    labels.append(label)

    # Add the legend to the side of the graph
    ax.legend(handles, labels, loc='center left', bbox_to_anchor=(1.0, 0.5))

    return (summary_mean, summary_std1, skewness, summary_variance, chisq)

class ICEDCamelPlotAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_LAYER = 'INPUT_LAYER'

    SampleField = 'SampleField'
    SiteField = 'SiteField'
    AgeField = 'AGEFIELD'
    ErrField = 'ERRFIELD'

    OUTPUT_FOLDER = 'OUTPUT_FOLDER'
    OUTPUT_FILE = 'OUTPUT_FILE'

    def initAlgorithm(self, config):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_LAYER,
                self.tr('Input ExpAge Data'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                self.SampleField,
                self.tr('Sample Name Field'),
                None, self.INPUT_LAYER, QgsProcessingParameterField.String))

        self.addParameter(
            QgsProcessingParameterField(
                self.SiteField,
                self.tr('Site Name Field'),
                None, self.INPUT_LAYER, QgsProcessingParameterField.String))

        self.addParameter(
            QgsProcessingParameterField(
                self.AgeField,
                self.tr('ExpAge Field'),
                None, self.INPUT_LAYER, QgsProcessingParameterField.Numeric))

        self.addParameter(
            QgsProcessingParameterField(
                self.ErrField,
                self.tr('Age Error Field'),
                None, self.INPUT_LAYER, QgsProcessingParameterField.Numeric))


        self.addParameter(
            QgsProcessingParameterFolderDestination(
                self.OUTPUT_FOLDER,
                self.tr('Camelplot Folder'),
                None))

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT_FILE, 
                self.tr('Output Site Point Features'), 
                type=QgsProcessing.TypeVectorPoint))


    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(parameters, self.INPUT_LAYER, context)
        if source is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT_LAYER))
            
        fields = QgsFields()
        fields.append(QgsField('id', QVariant.Int, '', 10, 0))
        fields.append(QgsField('SiteName', QVariant.String, '', 100))
        fields.append(QgsField('CamelPlot', QVariant.String, '', 100))
        fields.append(QgsField('SampleNum', QVariant.Int, '', 10, 0))
        fields.append(QgsField('Mean', QVariant.Double, 'double', 10, 1))
        fields.append(QgsField('STD', QVariant.Double, 'double', 10, 0))
        fields.append(QgsField('Variance', QVariant.Double, 'double', 10, 0))
        fields.append(QgsField('Skew', QVariant.Double, 'double', 10, 3))
        fields.append(QgsField('Chisq', QVariant.Double, 'double', 10, 3))

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUTPUT_FILE,
                #context, source.fields(), source.wkbType(), source.sourceCrs())
                context, fields, QgsWkbTypes.Point, source.sourceCrs())
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT_FILE))

        age_field = self.parameterAsString(parameters, self.AgeField, context)

        err_field = self.parameterAsString(parameters, self.ErrField, context)

        sample_field = self.parameterAsString(parameters, self.SampleField, context)

        site_field = self.parameterAsString(parameters, self.SiteField, context)
        
        outfolder = self.parameterAsFile (parameters, self.OUTPUT_FOLDER, context)
        
        #fieldnames = [field.name() for field in source.fields()]
        #fieldnames = ['name', 'site_name', 't_St','dtint_St']
        fieldnames = [sample_field, site_field, age_field, err_field, 'lon', 'lat']
        
        # Compute the number of steps to display within the progress bar and
        # get features from source
        total = 100.0 / source.featureCount() if source.featureCount() else 0
        features = source.getFeatures()


        ages = []
        errs = []
        samples = []
        sites = []
        Xs = []
        Ys = []
        
        for current, f in enumerate(features):
            # Stop the algorithm if cancel button has been clicked
            if feedback.isCanceled():
                break
            ##get the field as list
            ##Need to remove the potential null data
            if (str(f[fieldnames[3]]) != "NULL") and (float(f[fieldnames[3]])> 0):
                samples.append(f[fieldnames[0]])
                sites.append((f[fieldnames[1]]))
                ages.append((f[fieldnames[2]]))
                errs.append((f[fieldnames[3]]))
                Xs.append((f[fieldnames[4]]))
                Ys.append((f[fieldnames[5]]))
                
                # Update the progress bar
                feedback.setProgress(int(current * total))

        XsArr = np.array(Xs)
        YsArr = np.array(Ys)

        samplesArr = np.array(samples)
        agesArr = np.array(ages)
        errsArr = np.array(errs)
        sitesArr = np.array(sites)
        unique_sites = np.unique(sitesArr)
        stds_all = []
        skewall = []
        variance_all = []
        chiall = []
        sitePoints = []
        
        
        total = 100.0 / len(unique_sites) if len(unique_sites) else 0
        i = 0
        for site_name in unique_sites:

            site_ages = agesArr[sitesArr == site_name]
            site_errs = errsArr[sitesArr == site_name]
            site_samples = samplesArr[sitesArr == site_name]
            num = len(site_ages)
            
            fig, ax = plt.subplots()
            (summary_mean, summary_std1, skewness, summary_variance, chisq) = camelplot(site_ages/1000, site_errs/1000, site_samples, site_name, ax)
            chiall.append(chisq)
            stds_all.append(summary_std1)
            variance_all.append(summary_variance)
            skewall.append(skewness) 

            filename = outfolder + "\\Camelplot_" + site_name+".png"
            fig.savefig(filename, dpi=300, bbox_inches='tight')
            plt.close(fig)  # Close the figure to save computer processing            

            #Create the site point based on the averaged X and Y coordinate of the samples and add the point into the site feature class   
            site_Xs = XsArr[sitesArr == site_name]
            num = len(site_Xs)
            meanX = sum(site_Xs)/ num

            site_Ys = YsArr[sitesArr == site_name]
            meanY = sum(site_Ys)/ num
            
            point = QgsPoint(meanX, meanY)
            feats = QgsFeature()
            sitename = str(site_name)
            plotlink = "file:///" + outfolder + "\\Camelplot_" + site_name+".png"
            
            feats.setAttributes([i, sitename, plotlink, num, float(summary_mean), float(summary_std1), float(summary_variance), float(skewness), float(chisq)])
            feats.setGeometry(QgsGeometry(point))
            sink.addFeature(feats)
    
            # Update the progress bar
            feedback.setProgress(int(i * total))
            i += 1

        ##Summary Statistics for the whole datasets
        numsites = len(chiall)

        # Calculate the mean, std, min, max, and range of standard deviation histogram
        meanstd = np.mean(stds_all)
        std_stds = np.std(stds_all, ddof=1)
        min_std = np.min(stds_all)
        max_std = np.max(stds_all)
        range_std = max_std - min_std

        fig, ax = plt.subplots()

        ax.set_title('Standard Deviation Histogram')
        ax.set_xlabel(f'Standard Deviation, # Sites: {numsites}')
        ax.set_ylabel('Frequency')
        ax.hist(stds_all, bins=20, density=False, facecolor = '#2ab0ff', edgecolor='#169acf')
        ax.axvline(meanstd, color='r', linestyle='--', label=f"Mean={meanstd:.5f}")
        ax.axvline(meanstd+std_stds, color='g', linestyle='--', label=f"Std Dev={std_stds:.2f}")
        #ax.axvline(meanstd-std_stds, color='g', linestyle='--')
        ax.axvline(linestyle='None', label=f"Min={min_std:.2f}, Max={max_std:.2f}, Range={range_std:.2f}")
        ax.legend()
        #plt.show()

        filename = outfolder + "\\STD_histogram.png"
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)  # Close the figure to save computer processing    

        skewall = np.array(skewall)

        fig, bx = plt.subplots()
        #bx = fig.add_subplot(2, 2, 2)

        bx.set_title('Skew Histogram')
        bx.set_xlabel(f'Skew, # Sites: {numsites}')
        bx.set_ylabel('Frequency')

        # Calculate mean, max, min, range, and standard deviation of skew data and plot it
        mean = np.mean(skewall)
        std_dev = np.std(skewall)
        minall = np.max(skewall)
        maxall = np.min(skewall)
        rangeall = maxall-minall
        bx.hist(skewall, bins=30, density=False, facecolor='#2ab0ff', edgecolor='#169acf')
        bx.axvline(mean, color='r', linestyle='--', label=f"Mean={mean:.5f}")
        bx.axvline(mean+std_dev, color='g', linestyle='--', label=f"Std Dev={std_dev:.2f}")
        bx.axvline(mean-std_dev, color='g', linestyle='--')
        bx.axvline(linestyle='None', label=f"Min={minall:.2f}, Max={maxall:.2f}, Range={rangeall:.2f}")
        bx.legend()
        #plt.show()
        filename = outfolder + "\\Skew_histogram.png"
        #fig.savefig(f'lyk_{site_name}.png', dpi=300, bbox_inches='tight')
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)

        fig, cx = plt.subplots()
        #cx = fig.add_subplot(2, 2, 3)
        cx.set_title('Chi-Squared Histogram')
        cx.set_xlabel(f'Chi-Squared Value, # Sites: {numsites}')
        cx.set_ylabel('Frequency')
        mean_chi = np.mean(chiall)
        std_chi = np.std(chiall, ddof=1)
        minchi = np.min(chiall)
        maxchi = np.max(chiall)
        rangechi = maxchi - minchi
        cx.hist(chiall, bins=30, density=False, facecolor='#2ab0ff', edgecolor='#169acf')
        cx.axvline(mean_chi, color='r', linestyle='--', label=f"Mean={mean_chi:.5f}")
        cx.axvline(mean_chi+std_chi, color='g', linestyle='--', label=f"Std Dev={std_chi:.2f}")
        cx.axvline(mean_chi-std_chi, color='g', linestyle='--')
        cx.axvline(linestyle='None', label=f"Min={minchi:.2f}, Max={maxchi:.2f}, Range={rangechi:.2f}")
        cx.legend()

        ##Show the plots
        #plt.show()

        filename = outfolder + "\\Chi_Squared_histogram.png"
        #fig.savefig(f'lyk_{site_name}.png', dpi=300, bbox_inches='tight')
        fig.savefig(filename, dpi=300, bbox_inches='tight')
        plt.close(fig)

 
        return {self.OUTPUT_FILE: dest_id}    

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'Camel Plots'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr(self.name())

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr(self.groupId())

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return ''

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ICEDCamelPlotAlgorithm()

    def icon(self):
        cmd_folder = os.path.split(inspect.getfile(inspect.currentframe()))[0]
        icon = QIcon(os.path.join(os.path.join(cmd_folder, 'camellogo.png')))
        return icon