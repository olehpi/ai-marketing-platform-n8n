import {INodeType, INodeTypeDescription, ISupplyDataFunctions} from "n8n-workflow";
import {BridgeChatModelLLM} from "./BridgeChatModelLLM";

export class BridgeChatModel implements INodeType {
    description: INodeTypeDescription = {
        displayName: "Bridge AI Chat Model",
        name: "bridgeChatModel",
        icon: "file:bridge.svg",
        group: ["transform"],
        version: 1,
        description: "Telegram Bridge LangChain Chat Model",
        defaults: {name: "Bridge Chat Model"},
        inputs: [],
        outputs: ["ai_languageModel"],
        properties: [
            {
                displayName: "Bridge URL",
                name: "url",
                type: "string",
                default: "http://telegram_bridge:8000/chat",
                required: true
            }
        ]
    };

    async supplyData(this: ISupplyDataFunctions) {
        const url = this.getNodeParameter("url", 0) as string;
        return {response: new BridgeChatModelLLM(url)};
    }
}