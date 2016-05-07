/*
 rule.summary=FHIR Connectathon 12 - Track 08 FHIR Genomics - Scenario 02 Germline Testing Observation in Search
 rule.description=Verify that the Bundle contains at least one Observation containing Genomic Source Class extension and the germline code value = 'LA6683-2'
*/
assert contentType=='JSON' || contentType=='XML': "Expected JSON or XML in message body"

if (contentType=='JSON') {
	assert !body.resourceType.is(null) && !body.resourceType.isEmpty(): "Could not find resourceType in message body"
	assert body.resourceType.equals('Bundle'): "Expected Bundle resource in response but found '"+body.resourceType+"'"

	def germlineEntries = body.'**'.findAll { node ->
		node.name()=='extension' && node.@url=='http://hl7.org/fhir/StructureDefinition/observation-geneticsGenomicSourceClass' &&
		!node.valueCodeableConcept.isEmpty() && !node.valueCodeableConcept.coding.isEmpty() &&
		!node.valueCodeableConcept.coding.code.isEmpty() && node.valueCodeableConcept.coding.code.@value == 'LA6683-2'
	}
	assert germlineEntries.size() > 0: "Could not find Observation in searchset Bundle entries with Genomic Source Class extension and germline code value = 'LA6683-2'"
} else {
	assert !body.name().is(null) && !body.name().isEmpty(): "Could not find resource in message body"
	assert body.name().equals('Bundle'): "Expected Bundle resource in response but found '"+body.name()+"'"

	def germlineEntries = body.'**'.findAll { node ->
		node.name()=='extension' && node.@url=='http://hl7.org/fhir/StructureDefinition/observation-geneticsGenomicSourceClass' &&
		!node.valueCodeableConcept.isEmpty() && !node.valueCodeableConcept.coding.isEmpty() &&
		!node.valueCodeableConcept.coding.code.isEmpty() && node.valueCodeableConcept.coding.code.@value == 'LA6683-2'
	}
	assert germlineEntries.size() > 0: "Could not find Observation in searchset Bundle entries with Genomic Source Class extension and germline code value = 'LA6683-2'"
}