import {BaseChatModel, BaseChatModelParams,} from "@langchain/core/language_models/chat_models";
import {BaseMessage, AIMessage, HumanMessage, SystemMessage, ToolMessage} from "@langchain/core/messages";
import {ChatResult} from "@langchain/core/outputs";
import axios from "axios";

export interface BridgeTool {
    name: string;
    description?: string;
    parameters?: any;
}

export class BridgeChatModelLLM extends BaseChatModel {
    private tools: BridgeTool[] = [];

    constructor(private bridgeUrl: string,
                private botName: string,
                params?: BaseChatModelParams) {
        super(params ?? {});
        console.log("BridgeChatModel created: ", bridgeUrl);
        console.log("botName: ", botName);
    }

    /* LangChain tool binding */
    bindTools(tools: any[]) {
        console.log("Bridge tools:", tools.map(t => t.name));
        const model = new BridgeChatModelLLM(this.bridgeUrl, this.botName);
        model.tools = tools.map(
            tool => ({
                name: tool.name,
                description: tool.description,
                parameters: tool.schema ?? {}
            })
        );
        return model;
    }


    private serializeMessages(messages: BaseMessage[]) {
        return messages.map(
            msg => {
                let role = "assistant";
                if (msg instanceof HumanMessage)
                    role = "user";
                if (msg instanceof SystemMessage)
                    role = "system";
                if (msg instanceof ToolMessage)
                    role = "tool";
                return {
                    role,
                    content: msg.content
                };
            }
        );
    }

    async _generate(messages: BaseMessage[], options: any): Promise<ChatResult> {
        const body = {
            messages: this.serializeMessages(messages),
            tools: this.tools,
            bot_name: this.botName,
        };
        console.log("BRIDGE REQUEST", JSON.stringify(body, null, 2));
        const result = await axios.post(
            this.bridgeUrl,
            body,
            {timeout: 120000}
        );

        const data = result.data;
        console.log("BRIDGE RESPONSE", JSON.stringify(data, null, 2));

        /*  Tool call */
        if (data.tool_calls && data.tool_calls.length) {
            const message = new AIMessage({
                content: data.content ?? "",
                tool_calls: data.tool_calls.map(
                    (tool: any) => ({
                        id: tool.id ?? crypto.randomUUID(),
                        name: tool.name,
                        args: tool.arguments ?? tool.args ?? {}
                    })
                )
            });
            return {
                generations: [
                    {
                        text: "", message
                    }
                ]
            };
        }

        return {
            generations: [
                {
                    text: data.content ?? data.answer ?? "",
                    message: new AIMessage(data.content ?? data.answer ?? "")
                }
            ]
        };
    }

    _llmType() {
        return "bridge-chat-model";
    }

}